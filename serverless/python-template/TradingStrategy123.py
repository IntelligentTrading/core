import json
from StrategyHandler import AbstractStrategyHandler
import logging
logger = logging.getLogger('TradingStrategy123')
logger.setLevel(logging.INFO)


class TradingStrategy123(AbstractStrategyHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indicators = ["RSI", "SMA",]


    def make_signal(self) -> int:
        from StrategyHandler import BUY, SELL, IGNORE
        rsi = self.get_indicator("RSI")
        sma = self.get_indicator("SMA")

        if rsi > 70:
            self.signal = BUY
        else:
            self.signal = BUY

        return self.signal


def check_strategy_ABC(event, context):
    logger.info("\n-------------------\n" +
                "Trading Strategy ABC" +
                "\n-------------------")
    logger.info('Event: {e}\nContext: {c}'.format(e=event, c=context))
    try:
        logger.info("initiating objects...............")
        this_trading_strategy = TradingStrategy123(sns_context=context)
        logger.info("running..........................")
        this_trading_strategy.run()
        logger.info("saving...........................")
        this_trading_strategy.save()
    except Exception as e:
        logger.warning("Exception: {}".format(e))
    return
