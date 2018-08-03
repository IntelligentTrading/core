import logging
from apps.TA import TAException
from settings.redis_db import database, set_of_known_sets_in_redis
from apps.TA.storages.abstract.key_value import KeyValueStorage

logger = logging.getLogger(__name__)


class StorageException(TAException):
    pass

class VolumeseriesException(TAException):
    pass


class VolumeseriesStorage(KeyValueStorage):
    """
    stores things in a sorted set unique to each ticker and exchange
    ordered by blocks of volume as opposed to time
    todo: split the db by each exchange source
    todo: refactor to add short, medium, long (see resample_period in abstract_indicator)
    """
    class_describer = "volumeseries"