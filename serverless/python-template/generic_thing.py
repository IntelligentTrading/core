import json
import boto3


class NoContextException(Exception):
    pass


class AbstractThing(object):

    def __init__(self):
        sns_client = boto3.client('sns')
        self.context = {}

        self.horizon = self.context.horizon

    def load_context(self):
        if not len(self.context):
            raise NoContextException("function context must be included")

        try:
            self.sns_message = self.context['Records'][0]['Sns']['Message'][0]
        except KeyError as e:
            logger.error("SNS messages not found! Check code and configurations.")

        self.horizon = self.sns_message['horizon']
        



    def get_required_data(self):
        # connect to DB
        #




class AbstractStrategy(AbstractThing):

    def __init__(self, sns_content):
        super().__init__(sns_content)





# {'Records': [{
#     'EventSource': 'aws:sns',
#     'EventVersion': '1.0',
#     'EventSubscriptionArn': 'arn:aws:sns:us-east-1:983584755688:itt-sns-data-core-stage:493ba9a2-52f0-4c12-b1a4-7bdaee803690'
#         ,
#     'Sns': {
#         'Type': 'Notification',
#         'MessageId': 'dc693f13-b8d8-5445-88b1-6c9954471f92',
#         'TopicArn': 'arn:aws:sns:us-east-1:983584755688:itt-sns-data-core-stage'
#             ,
#         'Subject': None,
#         'Message': '[{"source": "binance", "category": "price", "symbol": "ETH/BTC", "value": 0.077133, "timestamp": 1527835230.836},
#
