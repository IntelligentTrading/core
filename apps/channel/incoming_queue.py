import logging
import time

import boto3

from settings import AWS_OPTIONS, DEBUG



logger = logging.getLogger(__name__)

if not DEBUG:
    logging.getLogger("botocore").setLevel(logging.INFO)


class SqsListener:

    def __init__(self, queue_name, **kwargs):
        """
        :param queue_name: name of sqs queue
        :param kwargs: settings for sqs listener, interval=10, region_name='us-east-1'
        """

        self._queue_name = queue_name
        self._region_name = kwargs.get('region_name', 'us-east-1')
        self._poll_interval = kwargs.get('interval', 10) # by default poll messages every 10 sec
        self._wait_time = kwargs.get('wait_time', 0) #in seconds, wait_time=0 mean short polling
        self.handler = lambda *args: None # empty handler

        self._client = self._init_sqs_client()

    def _init_sqs_client(self):
        self._session = boto3.Session(
            aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        )
        sqs = self._session.client('sqs', region_name=self._region_name)
        queues = sqs.list_queues(QueueNamePrefix=self._queue_name) # we filter to narrow down the list
        self._queue_url = queues['QueueUrls'][0]
        return sqs

    def listen(self):
        while True:
            # short polling if WaitTimeSecconds=0 or not specified
            # better use long polling
            messages = self._client.receive_message(
                QueueUrl=self._queue_url,
                WaitTimeSeconds=self._wait_time,
            )
            if 'Messages' in messages:
                logger.info(f"SQS messages received: {len(messages['Messages'])}")

                for message in messages['Messages']:
                    receipt_handle = message['ReceiptHandle']

                    self._client.delete_message(
                        QueueUrl=self._queue_url,
                        ReceiptHandle=receipt_handle
                    )

                    try:
                        self.handler(message['Body'])
                    except Exception:
                        logger.error(f"Error handling SQS message -> ReceiptHandle: {receipt_handle}")
                        logger.debug(f"MessageBody: {message['Body']}")

            else:
                time.sleep(self._poll_interval)
