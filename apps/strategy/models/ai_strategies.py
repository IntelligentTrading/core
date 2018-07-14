from apps.strategy.models.abstract_strategy import AbstractStrategy
import logging

logger = logging.getLogger(__name__)


class AnnSimpleStrategy(AbstractStrategy):
    strategy_signals_set = set(['ann_simple_bull', 'ann_simple_bear'])

    def __str__(self):
        return "AiSimpleStrategy"

    # TODO: make sure that signals go in order, i.e. buy/sell/buy/sell/...
    # by retrieving the previous signal in strategy

