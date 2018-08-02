import logging
from apps.TA import TAException
from settings.redis_db import database
from apps.TA.storages.abstract.indicator import TickerStorage
from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage


logger = logging.getLogger(__name__)


defualt_price_indexes = ["open_price", "close_price", "low_price", "high_price",]
derived_price_indexes = ["midpoint_price", "mean_price", "price_variance",]
default_volume_indexes = ["close_volume",]
derived_volume_indexes = ["open_volume", "low_volume", "high_volume",]
default_indexes = defualt_price_indexes + default_volume_indexes
derived_indexes = derived_price_indexes + derived_volume_indexes
all_indexes = default_indexes + derived_indexes

class PriceVolumeHistoryException(TAException):
    pass


class PriceVolumeHistoryStorage(TickerStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close_price")
        self.value = kwargs.get('value')


    @classmethod
    def query(cls, ticker, exchange=None, index="",
              timestamp=None, periods=0,
              *args, **kwargs):

        # "ETH_BTC:poloniex:PriceVolumeHistoryStorage:close_price"
        # f'{ticker}:{exchange}:{cls.__name__}:{index}'
        if not index:
            logger.debug("assuming to use `close_price` index in price query")
            index = "close_price"

        key_suffix = f':{index}'

        results_dict = super().query(ticker=ticker, exchange=exchange,
                                     key_suffix=key_suffix,
                                     timestamp=timestamp, periods=periods,
                                     *args, **kwargs)

        results_dict['index'] = index
        return results_dict


    def save(self, *args, **kwargs):

        # meets basic requirements for saving
        if not all([self.ticker, self.exchange,
                   self.index, self.value,
                   self.unix_timestamp]):
            logger.error("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceVolumeHistoryException("save error, missing data")

        if not self.force_save:
            if not self.index in defualt_price_indexes + default_volume_indexes:
                logger.error("price index not in approved list, raising exception...")
                raise PriceVolumeHistoryException("unknown index: " + str(self.index))

        self.db_key_suffix = f':{self.index}'
        logger.debug("ready to save, db_key will be " + self.get_db_key())
        return super().save(*args, **kwargs)
