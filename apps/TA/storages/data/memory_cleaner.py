import logging

from apps.TA import TAException
from apps.TA.storages.abstract.subscriber import TASubscriber
from apps.TA.storages.data.pv_history import PriceVolumeHistoryStorage, all_indexes
from settings.redis_db import database

logger = logging.getLogger(__name__)


class CleanerException(TAException):
    pass


class CleanerSubscriber(TASubscriber):

    classes_subscribing_to = [
        PriceVolumeHistoryStorage
    ]

    def handle(self, channel, data, *args, **kwargs):

        if channel == PriceVolumeHistoryStorage.__name__:
            try:
                # parse from data["key"] which should come like
                # f'{data_history.ticker}:{data_history.exchange}:{data_history.timestamp}'
                [ticker, exchange, timestamp] = data["key"].split(":")

            except Exception as e:
                raise CleanerException("PriceVolumeHistoryStorage key not recognized. " + str(e))

            else:

                for index in all_indexes:
                    sorted_set_key = f'{ticker}:{exchange}:PriceVolumeHistoryStorage:{index}'
                    database.zremrangebyscore(sorted_set_key, 0, int(timestamp)-(60*90))  # 90 minutes or older
