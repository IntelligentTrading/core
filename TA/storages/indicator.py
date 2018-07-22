from TA.app import logger, TAException
from TA.storages.timeseries_storage import TimeseriesStorage, TimeseriesException


class IndicatorException(TAException):
    pass


class TimeseriesTicker(TimeseriesStorage):
    """
    stores timeseries data on tickers in a sorted set unique to each ticker and exchange
    todo: split the db by each exchange source
    """
    describer_class = "ticker"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.describer_class = kwargs.get('describer_class', "ticker")

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


    def get_db_key(self):
        self.db_key_prefix = f'{self.ticker}:{self.exchange}:'
        # by default will return "{ticker}:{exchange}:{class_name}"
        return super().get_db_key()

    @classmethod
    def query(cls, ticker, exchange="", timestamp=None, key="", key_suffix=""):

        if not exchange:
            exchange = 'poloniex'

        key_prefix = f'{ticker}:{exchange}'

        return super().query(key=key, key_prefix=key_prefix, key_suffix=key_suffix, timestamp=timestamp)


class TimeseriesIndicator(TimeseriesTicker):
    """
    stores indicators in a sorted set unique to each ticker and exchange
    requires data to be a resampling to represent the most recent 5min block of time
    timestamp value must be evenly divisible by 5 minutes (300 seconds)
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.describer_class = kwargs.get('describer_class', "indicator")

        # ALL INDICATORS ARE ASSUMED 5-MIN PERIOD RESAMPLED
        if self.unix_timestamp % 300 != 0:
            raise TimeseriesException("indicator timestamp should be % 300")
        # self.resample_period = 300  # 5 min


"""
===== EXAMPLE USAGE =====

my_indicator = TimeseriesIndicator(ticker="ETH_BTC",
                                   exchange="BITTREX",
                                   timestamp=1483228800)
my_indicator.value = "BUY BITCOIN"
my_indicator.save()

# advanced:

very_special_signal = TimeseriesIndicator(describer_class="SuperSignal",
                                          key="SuperSignal",
                                          key_suffix="answer_to_the_universe",
                                          ticker="ETH_BTC",
                                          timestamp=1483228800
                                          )
from TA.app import database
pipeline = database.pipeline()
for thing in ['towel', 42, 'babelfish', 'vogon poetry']:
    very_special_signal.unix_timestamp += 300
    very_special_signal.value = thing
    pipeline = very_special_signal.save(pipeline)
pipeline.execute()

===== EXAMPLE USAGE =====
"""
