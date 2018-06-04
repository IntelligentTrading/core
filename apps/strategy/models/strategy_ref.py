import logging

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


def get_all_strategy_classes() -> object:
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

        # create a class object
        class_obj = getattr(module, class_name)

        # add to a final list
        strategy_object_list.append(class_obj)

    return strategy_object_list
