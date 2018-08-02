import logging
from apps.TA import TAException
from settings.redis_db import database
from abc import ABC

logger = logging.getLogger(__name__)


class StorageException(TAException):
    pass

class TimeseriesException(TAException):
    pass


class KeyValueStorage(ABC):
    """
    stores things in redis database given a key and value
    by default uses the instance class name as the key
    recommend to uniqely identify the instance with a key prefix or suffix
    prefixes are for more specific categories of objects (eg. woman:human:mammal:_class_ )
    suffixes are for specific attributes (eg. _class_:eye_color, _class_:age, etc)
    """
    def __init__(self, *args, **kwargs):
        self.force_save = kwargs.get('force_save', False)
        # key for redis storage
        self.db_key = kwargs.get('key', self.__class__.__name__)
        self.db_key_prefix = kwargs.get('key_prefix', "")
        self.db_key_suffix = kwargs.get('key_suffix', "")
        self.value = ""

    def __str__(self):
        return str(self.get_db_key())


    @classmethod
    def compile_db_key(cls, key="", key_prefix="", key_suffix=""):
        key = key or cls.__name__
        return str(
            f'{key_prefix.strip(":")}:' +
            f'{key.strip(":")}' +
            f':{key_suffix.strip(":")}'
        )


    def get_db_key(self):

        # default for self.db_key is already self.__class__.__name__
        return str(
            self.compile_db_key(
                key=self.db_key,
                key_prefix=self.db_key_prefix,
                key_suffix=self.db_key_suffix
            )
            # todo: add this line for using env in key
            # + f':{SIMULATED_ENV if SIMULATED_ENV != "PRODUCTION" else ""}'
        )


    def save(self, pipeline=None, *args, **kwargs):
        if not self.value:
            raise StorageException("no value set, nothing to save!")
        if not self.force_save:
            # validate some rules here?
            pass
        logger.debug(f'saving key, value: {self.get_db_key()}, {self.value}')
        return database.set(self.get_db_key(), self.value)

    def get_value(self, db_key="", *args, **kwargs):
        return database.get(db_key or self.get_db_key())
