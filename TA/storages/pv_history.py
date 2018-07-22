from TA.app import TAException, logger
from TA.storages.indicator import TimeseriesTicker
from TA.storages.timeseries_storage import TimeseriesStorage

price_indexes = [
    "open_price", "close_price", "low_price", "high_price",
    "midpoint_price", "mean_price", "price_variance",
]

volume_indexes = [
    "open_volume", "close_volume", "low_volume", "high_volume",
]


class PriceVolumeHistoryException(TAException):
    pass


class PriceVolumeHistoryStorage(TimeseriesTicker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close")
        self.value = kwargs.get('value')


    @classmethod
    def query(cls, ticker, exchange=None, index="close", timestamp=None):
        # "ETH_BTC:poloniex:PriceVolumeHistoryStorage:close_price"
        # f'{ticker}:{exchange}:{cls.__name__}:{index}'
        key_suffix = f':{index}'
        return super().query(ticker=ticker, exchange=None, timestamp=timestamp, key_suffix=key_suffix)


    def save(self):  # todo: add pipeline

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
        return super().save()  # todo: add pipeline=pipeline


class BlockchainStatsHistory(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
