from abc import ABC
import logging

from TA.app import TAException
from TA.storages.indicator import TimeseriesIndicator
from TA.storages.pv_history import price_indexes


class PriceException(TAException):
    pass


class PriceStorage(TimeseriesIndicator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close")
        self.value = kwargs.get('value')


    def save(self, pipeline):

        # meets basic requirements for saving
        if not all(self.ticker, self.exchange,
                   self.index, self.value,
                   self.unix_timestamp):
            logging.error("incomplete information, cannot save \n" + str(self.__dict__))
            raise PriceException("save error, missing data")

        if not self.force_save:
            if not self.index in price_indexes:
                logging.error("price index not in approved list, raising exception...")
                raise PriceException("unknown index")

        self.db_key_suffix = ":{index}".format(self.index)
        super().save(pipeline=pipeline)


class BlockchainStatsHistory(TimeseriesIndicator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
