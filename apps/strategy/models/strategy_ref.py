import logging
from django.db import models


logger = logging.getLogger(__name__)

# A data structure to keep all possible strategies in the system
from collections import namedtuple
SignalRefType = namedtuple(
    'SignalRefType',
    'name implementation_module_name implementation_class_name description generated '
)

# TODO: Add every new strategy here which is neccesary to backtes or emit signals
ALL_STRATEGIES = {
    'rsi_simple' : SignalRefType(
        name='RSI Simple',
        implementation_module_name='apps.strategy.models.rsi_sma_strategies',
        implementation_class_name='RsiSimpleStrategy',
        description='Buy at RSI < 25, sell at RSI > 80',
        generated = 'manual'
    ),
    'ichi_kumo_breakout' : SignalRefType(
        name='Ichimoku Kumo Breakout',
        implementation_module_name='apps.strategy.models.ichi_strategies',
        implementation_class_name='IchiKumoBreakoutStrategy',
        description='Buy at Ichimoku Kumo breakout up and sell at Ichimoku bearkout down',
        generated='manual'
    ),
    'ann_simple' : SignalRefType(
        name='ANN Simple',
        implementation_module_name='apps.strategy.models.ai_strategies',
        implementation_class_name='AnnSimpleStrategy',
        description='Buy if ANN predict price will grow  and sell if it predicts that price goes down',
        generated='manual'
    )

}

# TODO to be deleted if works fine / need to do the same for AI
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



def get_all_strategy_classes():
    '''
    :return: all strategies in the system as class objects
    '''
    import importlib
    strategy_object_list = []

    all_strategies = ALL_STRATEGIES.copy()
    while all_strategies:
        _, strategy = all_strategies.popitem()

        # convert string name to a class object
        module_name = strategy.implementation_module_name
        class_name = strategy.implementation_class_name
        module = importlib.import_module(module_name)
        class_obj = getattr(module, class_name)

        # add to a final list
        strategy_object_list.append(class_obj)

    return strategy_object_list
