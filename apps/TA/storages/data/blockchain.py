import logging
from apps.TA import TAException
from apps.TA.storages.abstract.timeseries_storage import TimeseriesStorage


logger = logging.getLogger(__name__)


class BlockchainHistoryException(TAException):
    pass


class BlockchainStatsHistory(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
