from django.db import models
from apps.indicator.models.abstract_indicator import AbstractIndicator
from apps.indicator.models import price_resampl
from settings import MODIFY_DB
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BenVolume(AbstractIndicator):
    ben_volume_value = models.FloatField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['transaction_currency', 'counter_currency', 'source', 'resample_period']),
        ]

    def compute_ben(self) -> float:
        pass
        # TODO Karle: Please put your all your calculation here
        # you can you use self.resample_period etc from parent class
        logger.info(" ----------   here we compute Ben   --------- ")
        return None


    @staticmethod
    def compute_all(cls, **kwargs):
        new_ben_instance = cls(**kwargs)
        ben_volume = new_ben_instance.compute_ben()

        # saving data into DB
        # MODIFY_DB is for debug mode, allows to run on local and do not modify DB
        if ben_volume and MODIFY_DB:
            new_ben_instance.save()
            logger.info("   ...Ben calculation completed and saved.")
        else:
            logger.info("       Ben was not saved (either no value or debug mode)")
