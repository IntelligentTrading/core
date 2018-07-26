from TA.app import logger, TAException
from TA.storages.abstract.timeseries_storage import TimeseriesStorage


class IndicatorException(TAException):
    pass


class TickerStorage(TimeseriesStorage):
    """
    stores timeseries data on tickers in a sorted set unique to each ticker and exchange
    todo: split the db by each exchange source
    """
    describer_class = "ticker"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.describer_class = kwargs.get('describer_class', self.__class__.describer_class)

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
    def query(cls, ticker, exchange="",
              key="", key_suffix="",
              timestamp=None, periods=0):

        if not exchange:
            exchange = 'poloniex'

        key_prefix = f'{ticker}:{exchange}'

        results_dict = super().query(key=key, key_prefix=key_prefix, key_suffix=key_suffix,
                                     timestamp=timestamp, periods=periods)

        results_dict['exchange'] = exchange
        results_dict['ticker'] = ticker
        return results_dict
