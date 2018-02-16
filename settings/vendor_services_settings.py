import os
from settings import LOCAL, PRODUCTION, STAGE


if PRODUCTION:
    BUCKET_NAME = "intelligenttrading-s3-production"
    QUEUE_NAME = "intelligenttrading-sqs-production" # for production bot
    # DELAYED_QUEUE_NAME = "intelligenttrading-delayed-sqs-production"
    BETA_QUEUE_NAME = "intelligenttrading-sqs-beta" # for beta bot
    TEST_QUEUE_NAME = ""
    SNS_NAME = "intelligenttrading-sns-production"

elif STAGE:
    BUCKET_NAME = "intelligenttrading-s3-stage"
    QUEUE_NAME = "intelligenttrading-sqs-stage" # for stage bot
    BETA_QUEUE_NAME = "" # intelligenttrading-sqs-stage-beta
    # DELAYED_QUEUE_NAME = "intelligenttrading-delayed-sqs-stage"
    TEST_QUEUE_NAME = ""
    SNS_NAME = "intelligenttrading-sns-stage"

else: # LOCAL
    pass # see local_settings.py


if not LOCAL:

    # AWS
    AWS_OPTIONS = {
        'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
        'AWS_STORAGE_BUCKET_NAME': BUCKET_NAME,
    }

    HOST_URL = 'http://' + BUCKET_NAME + '.s3.amazonaws.com'
    MEDIA_URL = 'http://' + BUCKET_NAME + '.s3.amazonaws.com/'
    AWS_STATIC_URL = 'http://' + BUCKET_NAME + '.s3.amazonaws.com/'
    #STATIC_ROOT = STATIC_URL = AWS_STATIC_URL
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    #STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
