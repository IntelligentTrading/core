from TA.app import logger, TAException, database, set_of_known_sets_in_redis
from TA.storages.abstract.key_value import KeyValueStorage


class StorageException(TAException):
    pass

class TimeseriesException(TAException):
    pass



class TimeseriesStorage(KeyValueStorage):
    """
    stores things in a sorted set unique to each ticker and exchange
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """
    describer_class = "timeseries"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.describer_class = kwargs.get('describer_class', self.__class__.describer_class)

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
        self.describer_key = describer_key or f'{self.__class__.describer_class}:{self.get_db_key()}'

        if self.describer_key not in set_of_known_sets_in_redis:
            database.sadd("sorted_sets", self.describer_key)
            set_of_known_sets_in_redis.add(self.describer_key)


    @classmethod
    def query(cls, key="", key_suffix="", key_prefix="", timestamp=None):

        sorted_set_key = cls.compile_db_key(key=key, key_prefix=key_prefix, key_suffix=key_suffix)
        # example key f'{key_prefix}:{cls.__name__}:{key_suffix}'

        # do a quick check to make sure this is a class of things we know is in existence
        describer_key = f'{cls.describer_class}:{sorted_set_key}'
        if describer_key not in set_of_known_sets_in_redis:
            if database.sismember("sorted_sets", describer_key):
                database.sadd("sorted_sets", describer_key)
            else:
                logger.warning("query made for unknown class type: " + str(describer_key))
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
        if pipeline is not None:
            logger.debug("added command to redis pipeline")
            return pipeline.zadd(*zadd_args)
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
