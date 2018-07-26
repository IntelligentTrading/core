import logging
from abc import ABC

from TA.app import TAException, database
from TA.storages.abstract.indicator import IndicatorStorage
from TA.storages.data.pv_history import price_indexes


class PriceException(TAException):
    pass


class DataSubscriber(ABC):

    def __init__(self):
        from TA.app import database
        self.pubsub = database.pubsub()

        from TA.storages.data.pv_history import PriceVolumeHistoryStorage
        self.pubsub.subscribe(PriceVolumeHistoryStorage.describer_class)

    # def go_go_go(self):
    #     data_event = self.pubsub.get_message()
    #
    #     timestamp = parse_out_timestamp(data_event['message'])
    #     # close to a five minute period mark? (+ or - 45 seconds)
    #     seconds_from_five_min = int(history_instance.timestamp)+45 % 300
    #     if seconds_from_five_min < 90:
    #         # we are close to a 5min marker, notify subscribers
    #         do something


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
