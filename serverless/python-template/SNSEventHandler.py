import logging
import json
import boto3
from datetime import datetime
import os
SNS_ARN = os.environ['SNS_ARN']


class ContextException(Exception):
    pass

class SNSMessageException(Exception):
    pass

class ITFSNSException(Exception):
    pass


class AbstractSNSEventHandler(ABC):
    '''
    Base class for ITF Events and Strategies
    triggered by an SNS message
    required
    '''

    sns_context = {}
    sns_subscribe_arn = ""
    sns_publish_topic_prefix = ""
    sns_publish_topic = "" # automatically set, but can be overwritten manually
    sns_client_response = None
    _parameters = None


    def __init__(self, *args, **kwargs):
        if 'sns_context' in kwargs:
            self.sns_context = kwargs['sns_context']

        self.sns_publish_topic_prefix = "itf-sns-sls-event-"


    @property
    def context(self):
        return None # :handwave: not the droid your looking for

    @context.setter
    def context(self, sns_context):
        try:
            self.sns_message = self.sns_context['Records'][0]['Sns']['Message'][0]
        except KeyError as e:
            logger.error("SNS messages not found! Check code and configurations.")

        # self.horizon = self.sns_message['horizon']
        # self._parameters = value


    def emit_sns_message(self, message_data={}):
        # message data must be json serializable and not empty
        if not message_data:
            raise SNSMessageException("message_data is empty or missing!")
        try:
            json.dumps(message_data)
        except Exception as e:
            raise SNSMessageException(str(e))

        sns_subscribed_arn = self.sns_context['Records'][0]['Sns']['TopicArn']

        if not self.self.sns_publish_topic.startswith("itf-sns-"):
            # use instance class name
            self.sns_publish_topic = self.sns_publish_topic_prefix
            self.sns_publish_topic += str(c.__class__.__name__).lower()

        if not self.self.sns_publish_topic.startswith("itf-sns-"):
            raise ITFSNSException("SNS topic must start with 'itf-sns-'")

        sns_publishing_arn = ":".join(arn.split(":")[0:-1].append(self.sns_publish_topic))

        logging.info("Received message from SNS ARN {}".format(sns_subscribed_arn))
        logging.info("Publishing message to SNS ARN {}".format(sns_publishing_arn))

        sns_client = boto3.client('sns')
        self.sns_client_response = sns_client.publish(
            TargetArn=arn,
            Message=json.dumps({'default': json.dumps(message_data)}),
            MessageStructure='json'
        )
        


#
# EXAMPLE SNS MESSAGE FROM DATA APP ON HEROKU
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
