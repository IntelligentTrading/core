import logging

from TA.app import TAException
from TA.storages.abstract.indicator import IndicatorStorage
from TA.storages.data.pv_history import price_indexes


class PriceException(TAException):
    pass


class PriceStorage(IndicatorStorage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = kwargs.get('index', "close_price")
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
        return super().save(pipeline=pipeline)


class BlockchainStatsHistory(IndicatorStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
