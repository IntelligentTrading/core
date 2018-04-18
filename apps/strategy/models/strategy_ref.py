import logging
from django.db import models

logger = logging.getLogger(__name__)


class StrategyRef(models.Model):
    '''
    Strategy class contains a Reference list of all Strategies and their meta-information
    The actual implementation is in separate classes
    '''

    name = models.CharField(max_length=64, null=False, blank=False)
    implementation_module_name = models.CharField(max_length=128, null=True)
    implementation_class_name = models.CharField(max_length=64, null=True)
    description = models.TextField(null=True)

    generated = models.CharField(max_length=16, null=False, blank=False) # manual/auto
    last_backtested_performance = models.FloatField(null=True)



# get all class names
def get_all_strategy_classes():
    '''
    :return: all strategies in the system as class objects
    '''
    import importlib
    strategy_object_list = []
    strategy_string_list = list(StrategyRef.objects.all().values('implementation_module_name','implementation_class_name'))

    for strategy in strategy_string_list:
        module_name = strategy['implementation_module_name']
        class_name = strategy['implementation_class_name']
        module = importlib.import_module(module_name)
        class_obj = getattr(module, class_name)
        strategy_object_list.append(class_obj)

    return strategy_object_list


# pre-population of all strategies
def add_all_strategies():
    #TODO: check id DB is emtty, if so add strategies
    s1 = StrategyRef(
        name='RSI Simple',
        implementation_module_name='apps.strategy.models.rsi_sma_strategies',
        implementation_class_name='RsiSimpleStrategy',
        description='Buy at RSI < 25, sell at RSI > 80',
        generated = 'manual'
    )
    s1.save()

    return get_all_strategy_classes()