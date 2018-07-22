from TA.app import logger, TAException, database, set_of_known_sets_in_redis
from abc import ABC

class StorageException(TAException):
    pass

class TimeseriesException(TAException):
    pass


class RedisStorage(ABC):
    """
    stores things in redis database given a key and value
    by default uses the instance class name as the key
    recommend to uniqely identify the instance with a key prefix or suffix
    prefixes are for more specific categories of objects (eg. woman:human:mammal:_class_ )
    suffixes are for specific attributes (eg. _class_:eye_color, _class_:age, etc)
    """
    def __init__(self, *args, **kwargs):
        self.force_save = kwargs.get('force_save', False)
        # key for redis storage
        self.db_key = kwargs.get('key', self.__class__.__name__)
        self.db_key_prefix = kwargs.get('key_prefix', "")
        self.db_key_suffix = kwargs.get('key_suffix', "")
        self.value = ""

    def __str__(self):
        return str(self.get_db_key())


    @classmethod
    def compile_db_key(cls, key="", key_prefix="", key_suffix=""):
        key = key or cls.__name__
        return str(
            f'{key_prefix.strip(":")}:' +
            f'{key.strip(":")}' +
            f':{key_suffix.strip(":")}'
        )


    def get_db_key(self):

        # default for self.db_key is already self.__class__.__name__
        return str(
            self.compile_db_key(
                key=self.db_key,
                key_prefix=self.db_key_prefix,
                key_suffix=self.db_key_suffix
            )
            # todo: add this line for using env in key
            # + f':{SIMULATED_ENV if SIMULATED_ENV != "PRODUCTION" else ""}'
        )


    def save(self, pipeline=None):
        if not self.value:
            raise StorageException("no value set, nothing to save!")
        if not self.force_save:
            # validate some rules here?
            pass
        return database.set(self.get_db_key(), self.value)

    def get_value(self, db_key=""):
        return database.get(db_key or self.get_db_key())


class TimeseriesStorage(RedisStorage):
    """
    stores things in a sorted set unique to each ticker and exchange
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """
    describer_class = "timeseries"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.describer_class = kwargs.get('describer_class', "timeseries")

        # 'timestamp' REQUIRED, VALIDATE
        try:
            self.unix_timestamp = int(kwargs['timestamp'])  # int eg. 1483228800
        except KeyError:
            raise TimeseriesException("timestamp required for TimeseriesStorage objects")
        except ValueError:
            raise TimeseriesException(
                "timestamp must be castable as integer, received {ts}".format(
                    ts=kwargs.get('timestamp')))
        except Exception as e:
            raise StorageException(str(e))

        if self.unix_timestamp < 1483228800:
            raise TimeseriesException("timestamp before January 1st, 2017")


    def save_own_existance(self, describer_key=""):
        self.describer_key = describer_key or f'{self.describer_class}:{self.get_db_key()}'

        if self.describer_key not in set_of_known_sets_in_redis:
            database.sadd("sorted_sets", self.describer_key)
            set_of_known_sets_in_redis.add(self.describer_key)


    @classmethod
    def query(cls, key="", key_suffix="", key_prefix="", timestamp=None):

        sorted_set_key = cls.compile_db_key(key=key, key_prefix=key_prefix, key_suffix=key_suffix)
        # example key f'{key_prefix}:{cls.__name__}:{key_suffix}'

        # do a quick check to make sure this is a class of things we know is in existence
        describer_key = f'timeseries:{sorted_set_key}'
        if describer_key not in set_of_known_sets_in_redis:
            if database.sismember("sorted_sets", describer_key):
                database.sadd("sorted_sets", describer_key)
            else:
                return {'error': "class type is unknown to database"}

        # if no timestamp, assume query to find the most recent, the last one
        if not timestamp:
            query_response = database.zrange(sorted_set_key, -1, -1)
        else:
            query_response = database.zrangebyscore(sorted_set_key, timestamp - 1800, timestamp, 0, 1)

        # example query_response = [b'0.06288:1532163247']
        # which came from f'{self.value}:{str(self.unix_timestamp)}'
        try:
            [value, timestamp] = query_response[0].decode("utf-8").split(":")
            return {
                'value': value,
                'timestamp': timestamp
            }
        except IndexError:
            return None  # no problem, query just returned no results
        except Exception as e:
            logger.error("redis query problem: " + str(e))
            raise TimeseriesException(str(e))  # wtf happened?


    def save(self, pipeline=None):
        if not self.value:
            raise StorageException("no value set, nothing to save!")
        if not self.force_save:
            # validate some rules here?
            pass

        self.save_own_existance()
        # example >>> redis.zadd('my-key', 'name1', 1.1)
        zadd_args = (self.get_db_key(), # set key name
                      f'{self.value}:{str(self.unix_timestamp)}', # item unique value
                      int(self.unix_timestamp) # timestamp as score (int or float)
                     )
        logger.debug("saving data with args " + str(zadd_args))
        if pipeline:
            pipeline.zadd(*zadd_args)
            logger.debug("added command to redis pipeline")
            return pipeline
        else:
            logger.debug("no pipeline, executing zadd command immediately.")
            return database.zadd(*zadd_args)

    def get_value(self):
        TimeseriesException("function not yet implemented! ¯\_(ツ)_/¯ ")
        pass

"""
We can scan the newest or oldest event ids with ZRANGE 4,
maybe later pulling the events themselves for analysis.

We can get the 10 or even 100 events immediately
before or after a timestamp with ZRANGEBYSCORE
combined with the LIMIT argument.

We can count the number of events that occurred
in a specific time period with ZCOUNT.

https://www.infoq.com/articles/redis-time-series
"""
