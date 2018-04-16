import logging
from django.db import models

logger = logging.getLogger(__name__)


class StrategyRef(models.Model):
    '''
    Strategy class lists all Strategies and stores their meta-information
    The actual implementation is in separate classes
    '''

    name = models.CharField(max_length=64, null=False, blank=False)
    implementation_class_name = models.CharField(max_length=64, null=True)
    description = models.TextField(null=True)

    generated = models.CharField(max_length=16, null=False, blank=False) # manual/auto
    last_backtested_performance = models.FloatField(null=True)



# get all class names
def get_all_strategy_classes():
    from apps.strategy.models.rsi_sma_strategies import RsiSimpleStrategy, SmaCrossOverStrategy
    # retrieve from DB all claas names for futher itaration like

    return [RsiSimpleStrategy, SmaCrossOverStrategy]
