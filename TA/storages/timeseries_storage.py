from TA.app import logger, TAException, database, set_of_known_sets_in_redis
from abc import ABC

class StorageException(TAException):
    pass

class TimeseriesException(TAException):
    pass


class RedisStorage(ABC):

    def __init__(self, *args, **kwargs):
        self.force_save = kwargs.get('force_save', False)
        # key for redis storage
        self.db_key = kwargs.get('key', self.__class__.__name__)
        self.db_key_prefix = kwargs.get('key_prefix', "")
        self.db_key_suffix = kwargs.get('key_suffix', "")
        self.value = ""

    def __str__(self):
        return str(self.get_db_key())

    def get_db_key(self):
        if not self.value:
            raise StorageException("no value set, nothing to save!")
        if not self.force_save:
            # validate some rules here?
            pass

        # default for self.db_key is already self.__class__.__name__
        return str(
            f'{self.db_key_prefix.strip(":")}:' +
            f'{self.db_key.strip(":")}' +
            f':{self.db_key_suffix.strip(":")}'
            # todo: add this line for using env in key
            # + f':{SIMULATED_ENV if SIMULATED_ENV != "PRODUCTION" else ""}'
        )

    def save(self, pipeline=None):
        return database.set(self.get_db_key(), self.value)

    def get_value(self, db_key=""):
        return database.get(db_key or self.get_db_key())


class TimeseriesStorage(RedisStorage):
    """
    stores things in a sorted set unique to each ticker and exchange
    redis keys
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """

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


    def save(self, pipeline=None):
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
