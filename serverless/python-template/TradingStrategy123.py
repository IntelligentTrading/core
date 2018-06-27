import json

import logging
logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


class TradingStrategy123(AbstractStrategyHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indicators = ["RSI", "SMA",]


    def get_signal(self) -> int:
        (BUY, SELL, IGNORE) = (1,-1,0)
        rsi = self.get_indicator("RSI")
        sma = self.get_indicator("SMA")

        if rsi > 70:
            return BUY
        else:
            return BUY


def check_strategy_ABC(event, context):
    logger.info('Event: {e}\nContext: {c}'.format(e=event, c=context))
    try:
        this_trading_strategy = TradingStrategy123(sns_context=context)
        this_trading_strategy.run()
        this_trading_strategy.save()
    except Exception:
        logger.warning('Event: {e}\nContext: {c}'.format(e=event, c=context))
    return
