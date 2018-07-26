from TA.api import TAException, logger
from TA.storages.abstract.timeseries_storage import TimeseriesStorage


class BlockchainHistoryException(TAException):
    pass


class BlockchainStatsHistory(TimeseriesStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
