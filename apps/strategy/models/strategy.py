import logging
from django.db import models

logger = logging.getLogger(__name__)


class Strategy(models.Model):
    '''
    Strategy class stores the meta-information about all Strageties
    we have in the system
    The actual implementation is in separate classes
    '''

    name = models.CharField(max_length=32, null=False, blank=False)
    generated = models.CharField(max_length=16, null=False, blank=False) # manual/auto
    last_backtested_performance = models.FloatField(null=True)
    implementation_class_name = models.CharField(max_length=64, null=True)
