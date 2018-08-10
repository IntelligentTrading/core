import json
import logging
from apps.TA import TAException, JAN_1_2017_TIMESTAMP
from settings.redis_db import database, set_of_known_sets_in_redis
from apps.TA.storages.abstract.key_value import KeyValueStorage

logger = logging.getLogger(__name__)


class StorageException(TAException):
    pass

class TimeseriesException(TAException):
    pass



class TimeseriesStorage(KeyValueStorage):
    """
    stores things in a sorted set unique to each ticker and exchange
    todo: split the db by each exchange source

    """
    class_describer = "timeseries"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_describer = kwargs.get('class_describer', self.__class__.class_describer)

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

        if self.unix_timestamp < JAN_1_2017_TIMESTAMP:
            raise TimeseriesException("timestamp before January 1st, 2017")


    def save_own_existance(self, describer_key=""):
        self.describer_key = describer_key or f'{self.__class__.class_describer}:{self.get_db_key()}'

        if self.describer_key not in set_of_known_sets_in_redis:
            database.sadd("sorted_sets", self.describer_key)


    @classmethod
    def query(cls, key: str = "", key_suffix: str = "", key_prefix: str = "",
              timestamp: int = None, periods_range: int = 0,
              timestamp_tolerance: int = 299,
              *args, **kwargs) -> dict:

        sorted_set_key = cls.compile_db_key(key=key, key_prefix=key_prefix, key_suffix=key_suffix)
        logger.debug(f'query for sorted set key {sorted_set_key}')
        # example key f'{key_prefix}:{cls.__name__}:{key_suffix}'

        # do a quick check to make sure this is a class of things we know is in existence
        describer_key = f'{cls.class_describer}:{sorted_set_key}'
        if describer_key not in set_of_known_sets_in_redis:
            if database.sismember("sorted_sets", describer_key):
                database.sadd("sorted_sets", describer_key)
            else:
                logger.warning("query made for unrecognized class type: " + str(describer_key))
                return {'error': "class type is unrecognized to database"}

        # if no timestamp, assume query to find the most recent, the last one
        if not timestamp:
            query_response = database.zrange(sorted_set_key, -1, -1)

        if timestamp or periods_range:
            if not timestamp:
                try:
                    [value, timestamp] = query_response[0].decode("utf-8").split(":")
                except:
                    # force no results, which raises IndexError exception later
                    timestamp = JAN_1_2017_TIMESTAMP  # 1483228800

            max_timestamp = timestamp = int(timestamp) + timestamp_tolerance
            min_timestamp = max_timestamp - ((periods_range*300) + timestamp_tolerance)
            query_response = database.zrangebyscore(sorted_set_key, min_timestamp, max_timestamp)

        periods_range = periods_range or 1

        # example query_response = [b'0.06288:1532163247']
        # which came from f'{self.value}:{str(self.unix_timestamp)}'
        try:
            if timestamp == JAN_1_2017_TIMESTAMP:
                values = []
            else: # we are returning a list
                values = [vt.decode("utf-8").split(":")[0] for vt in query_response ]
                timestamps = [vt.decode("utf-8").split(":")[1] for vt in query_response ]
                #  todo: double check that [-1] in list is most recent timestamp

            if periods_range:
                if len(values) < periods_range:
                    "Sorry we couldn't find enough values for you :("


            return {
                'values': values,
                'values_count': len(values),
                'timestamp': timestamp,
                'earliest_timestamp': timestamps[0],
                'latest_timest': timestamps[-1],
                'periods_range': periods_range,
                'period_size': "300" if periods_range else None,
            }

        except IndexError:
            return None  # no problem, query just returned no results
        except Exception as e:
            logger.error("redis query problem: " + str(e))
            raise TimeseriesException(str(e))  # wtf happened?


    def save(self, publish=False, pipeline=None, *args, **kwargs):
        if not self.value:
            raise StorageException("no value set, nothing to save!")
        if not self.force_save:
            # validate some rules here?
            pass

        self.save_own_existance()

        z_add_key = self.get_db_key() # set key name
        z_add_name = f'{self.value}:{str(self.unix_timestamp)}' # item unique value
        z_add_score = int(self.unix_timestamp) # timestamp as score (int or float)
        z_add_data = {"key":z_add_key, "name":z_add_name, "score":z_add_score}  # key, score, name
        logger.debug(f'saving data with args {z_add_data}')

        if pipeline is not None:
            logger.debug("added command to redis pipeline")
            if publish:
                pipeline = pipeline.publish(self.__class__.__name__, json.dumps(z_add_data))
            return pipeline.zadd(*z_add_data.values())

        else:
            logger.debug("no pipeline, executing zadd command immediately.")
            response = database.zadd(*z_add_data.values())
            if publish:
                database.publish(self.__class__.__name__, json.dumps(z_add_data))
            return response


    def get_value(self, *args, **kwargs):
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
