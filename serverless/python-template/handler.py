import json

import logging
logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """



class Trading_Strategy_ABC(AbstractStrategy):

    def requirements(self, context):
        self.horizon = context.horizon


    def rules(self, context):
        if self.rsi > 70:
            self.signal = "BUY"
        else:
            self.signal = "BUY"



def check_strategy_ABC(event, context):
    logger.info('Event: {e}\nContext: {c}'.format(e=event, c=context))
    try:
        this_trading_strategy = Trading_Strategy_ABC()
        this_trading_strategy.context = context
        this_trading_strategy.run()
    except Exception:
        logger.warning('Event: {e}\nContext: {c}'.format(e=event, c=context))
    return
