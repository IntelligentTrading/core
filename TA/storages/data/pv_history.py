from TA.app import TAException, logger, database
from TA.storages.abstract.indicator import TickerStorage
from TA.storages.abstract.timeseries_storage import TimeseriesStorage


price_indexes = [
    "open_price", "close_price", "low_price", "high_price",
    "midpoint_price", "mean_price", "price_variance",
]

volume_indexes = [
    "open_volume", "close_volume", "low_volume", "high_volume",
]


class PriceVolumeHistoryException(TAException):
    pass


class PriceVolumeHistoryStorage(TickerStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close_price")
        self.value = kwargs.get('value')


    @classmethod
    def query(cls, ticker, exchange=None, index="", timestamp=None, periods=0):
        # "ETH_BTC:poloniex:PriceVolumeHistoryStorage:close_price"
        # f'{ticker}:{exchange}:{cls.__name__}:{index}'
        if not index:
            logger.debug("assuming to use `close_price` index in price query")
            index = "close_price"

        key_suffix = f':{index}'

        results_dict = super().query(ticker=ticker, exchange=exchange,
                                     key_suffix=key_suffix,
                                     timestamp=timestamp, periods=periods)

        results_dict['index'] = index
        return results_dict


    def save(self, pipeline=None):

        # meets basic requirements for saving
        if not all([self.ticker, self.exchange,
                   self.index, self.value,
                   self.unix_timestamp]):
            logger.error("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceVolumeHistoryException("save error, missing data")

        if not self.force_save:
            if not self.index in price_indexes + volume_indexes:
                logger.error("price index not in approved list, raising exception...")
                raise PriceVolumeHistoryException("unknown index: " + str(self.index))

        self.db_key_suffix = f':{self.index}'
        logger.debug("ready to save, db_key will be " + self.get_db_key())
        return super().save(pipeline=pipeline)


class BlockchainStatsHistory(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

