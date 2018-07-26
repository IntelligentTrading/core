from TA.api import TAException, logger
from TA.storages.abstract.indicator import IndicatorStorage


class BlockchainHistoryException(TAException):
    pass


class BlockchainHistory(IndicatorStorage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
