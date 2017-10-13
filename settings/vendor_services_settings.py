import os
from settings import LOCAL, PRODUCTION, STAGE


# AWS S3 info
if PRODUCTION:
    BUCKET_NAME = "intelligenttrading-s3-production"
    QUEUE_NAME = "intelligenttrading-sqs-production"
    # DELAYED_QUEUE_NAME = "intelligenttrading-delayed-sqs-production"
else:
    BUCKET_NAME = "intelligenttrading-s3-stage"
    QUEUE_NAME = "intelligenttrading-sqs-stage"
    # DELAYED_QUEUE_NAME = "intelligenttrading-delayed-sqs-stage"


HOST_URL = 'http://' + BUCKET_NAME + '.s3.amazonaws.com'


if not LOCAL:
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    MEDIA_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    AWS_STATIC_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    STATIC_ROOT = STATIC_URL = AWS_STATIC_URL
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
