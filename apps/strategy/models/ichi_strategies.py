from apps.strategy.models.abstract_strategy import AbstractStrategy
from apps.signal.models.signal import get_all_signals_names_now, get_signals_ts
import logging
logger = logging.getLogger(__name__)



class IchiKumoBreakoutStrategy(AbstractStrategy):
    strategy_signals_set = set(['ichi_kumo_up', 'ichi_kumo_down'])

    def __str__(self):
        return "IchiKumoBreakoutStrategy"

    #TODO: make sure that signals go in order, i.e. buy/sell/buy/sell/...
    # by retrieving the previous signal in strategy

