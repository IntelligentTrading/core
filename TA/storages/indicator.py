from TA.app import logger, TAException
from TA.storages.abstract_timeseries_storage import TimeseriesStorage, TimeseriesException


class IndicatorException(TAException):
    pass


class TimeseriesIndicatorStorage(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__()

        # 'ticker' REQUIRED
        # 'exchange EXPECTED BUT CAN STILL SAVE WITHOUT
        try:
            self.ticker = kwargs['ticker']  # str eg. BTC_USD
            self.exchange = str(kwargs.get('exchange', ""))  # str or int
        except KeyError:
            raise TAException("Indicator requires a ticker as initial parameter!")
        except Exception as e:
            raise TAException(str(e))
        else:
            if self.ticker.find("_") <= 0:
                raise TAException("ticker should be like BTC_USD")
            if not self.exchange:
                logger.debug("----- NO 'exchange' VALUE! ARE YOU SURE? -----")

        # ALL INDICATORS ARE ASSUMED 5-MIN PERIOD RESAMPLED
        if self.unix_timestamp % 300 != 0:
            raise TimeseriesException("indicator timestamp should be % 300")
        # self.resample_period = 300  # 5 min


    def get_db_key(self):
        self.db_key_prefix = f'{self.ticker}:{self.exchange}:'
        # by default will return "{ticker}:{exchange}:{class_name}"
        return super().get_db_key()


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
