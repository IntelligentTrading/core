from abc import ABC
import logging

from TA.app import TAException
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


class PriceVolumeHistoryStorage(TimeseriesStorage):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.index = kwargs.get('index', "close")
        self.value = kwargs.get('value')


    def save(self, pipeline):

        # meets basic requirements for saving
        if not all(self.ticker, self.exchange,
                   self.index, self.value,
                   self.unix_timestamp):
            logging.error("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceVolumeHistoryException("save error, missing data")

        if not self.force_save:
            if not self.index in price_indexes:
                logging.error("price index not in approved list, raising exception...")
                raise PriceVolumeHistoryException("unknown index")

        self.db_key_suffix = ":{index}".format(self.index)
        super().save(pipeline=pipeline)


class BlockchainStatsHistory(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__()
