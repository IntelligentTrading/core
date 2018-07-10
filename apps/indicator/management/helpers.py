import boto3
from datetime import datetime
import logging
import time

from apps.indicator.models import PriceResampl, PriceHistory, Volume

from settings import AWS_OPTIONS, BUCKET_NAME



logging.getLogger('botocore').setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

class DataFiller():
    # def f_func(item):
    #     print(item.__dict__)
    #
    # df = DataFiller('fill_pr', 10)
    # last_timestamp = df.state or datetime.now()
    # df.input_queryset = PriceResampl.objects.filter(close_volume__isnull=True, close_price__isnull=False, timestamp__lte=last_timestamp).order_by('-timestamp')
    # df.filler_function = f_func
    # df.run()

    def __init__(self, name, iterations=None, save_state_every=None):
        self.name = name
        self.iterations = iterations or 1000
        self.state = read_state_from_s3(name)
        self.state_property = None
        self.save_state_every = save_state_every
        self.input_queryset = None
        self.filler_function = None

    def run(self):
        print(f"Starting {self.name} from state {self.state}")
        iterated = False
        start_time = time.time()
        for idx, item in enumerate(self.input_queryset[:self.iterations].iterator()):
            iterated = True
            try:
                self.filler_function(item)
            except Exception as e:
                logger.error(f"Error inside filler function {self.filler_function}: {e}")

            if isinstance(self.save_state_every, int) and (idx % self.save_state_every == 0):
                save_state_to_s3(getattr(item, self.state_property), self.name)

        if not iterated:
            logger.info(">>>All Done. No more records<<<")
        else:
            logger.info(f">>> Processed {idx+1} records in {int(time.time() - start_time)} seconds")



def aws_client(resource_type):
    return boto3.client(
        resource_type,
        aws_access_key_id=AWS_OPTIONS['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=AWS_OPTIONS['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1',
    )

def save_state_to_s3(value, key):
    return aws_client('s3').put_object(
        Bucket=BUCKET_NAME,
        Body=str(value),
        Key=key
    )

def read_state_from_s3(key):
    try:
        return aws_client('s3').get_object(Bucket=BUCKET_NAME, Key=key)['Body'].read().decode('ascii')
    except Exception as e:
        logger.info(f"Can't read from S3:{key} - {e}")
        return None
