import json
from StrategyHandler import AbstractStrategyHandler
import logging
import deap
from deap import base, creator, gp

from GeneticProgram import GeneticProgram
logger = logging.getLogger('TradingStrategy123')
logger.setLevel(logging.INFO)


class GeneticStrategy(AbstractStrategyHandler, GeneticProgram):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        GeneticProgram.__init__(self)
        self.individual = kwargs['individual']
        # self.indicators = ["RSI", "SMA",]  # this would shadow the indicators dict in the super class, removed


    def make_signal(self) -> int:
        from StrategyHandler import BUY, SELL, IGNORE
        doge = gp.compile(self.individual, self.pset)
        outcome = doge([123])
        if outcome == self.buy:
            self.signal = BUY
        elif outcome == self.sell:
            self.signal = SELL
        elif outcome == self.ignore:
            self.signal = IGNORE
        else:
            raise Exception("Unknown outcome produced by doge baby... singularity?!?")

        return self.signal

    def rsi(self, input):
        return self.get_indicator("RSI")

    def sma50(self, input):
        return self.get_indicator("RSI")

    def ema50(self, input):
        return self.get_indicator("RSI")

    def sma200(self, input):
        return self.get_indicator("RSI")

    def ema200(self, input):
        return self.get_indicator("RSI")

    def price(self, input):
        return 50




def check_strategy_gp(event, context):
    logger.info("\n-------------------\n" +
                "Trading Strategy GP" +
                "\n-------------------")
    logger.info('Event: {e}\nContext: {c}'.format(e=event, c=context))
    try:
        logger.info("initiating objects...............")
        mock_individual = 'if_then_else(gt(price(ARG0), sma50(ARG0)), if_then_else(gt(17.64793885409774, 84.48578956778925), ' \
                          'if_then_else(True, ignore, ignore), sell), if_then_else(and_(True, False), ' \
                          'if_then_else(True, sell, ignore), if_then_else(True, buy, ignore)))'
        mock_individual = 'if_then_else(gt(price(ARG0), sma50(ARG0)), buy, sell)'
        this_trading_strategy = GeneticStrategy(sns_context=context, individual=mock_individual)
        logger.info("running..........................")
        this_trading_strategy.run()
        logger.info("saving...........................")
        this_trading_strategy.save()
    except Exception as e:
        logger.warning("Exception: {}".format(e))
    return
