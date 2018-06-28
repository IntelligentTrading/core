from apps.strategy.models.abstract_strategy import AbstractStrategy

import logging
logger = logging.getLogger(__name__)

################ Pattern for other strategies  #################
class BenVolumeBasedStrategy(AbstractStrategy):
    '''
    select a subset of already generated signals from the Signal class
    that subset shall represent a given strategy, for example for RsiSimple  as follows:
    - RSI simple strategy is buy when RSI < 25 and sell when RSI > 85
    '''

    # list of signals belonging to this strategy
    # NOTE: check signals.ALL_SIGNALS namedtuple
    strategy_signals_set = set(['rsi_sell_3', 'vbi_buy'])

    def __str__(self):
        return "BenVolumeBasedStrategy"