import os
from settings import LOCAL, PRODUCTION, STAGE


# AWS S3 info
if PRODUCTION:
    BUCKET_NAME = "itt-production"
    QUEUE_NAME = "IttQueue-production"
    DELAYED_QUEUE_NAME = "IttDelayedQueue-production"
elif STAGE:
    BUCKET_NAME = "itt-stage"
    QUEUE_NAME = "IttQueue-stage"
    DELAYED_QUEUE_NAME = "IttDelayedQueue-stage"
else:
    BUCKET_NAME = os.environ.get("BUCKET_NAME", "itt-stage")
    BUCKET_NAME = BUCKET_NAME
    QUEUE_NAME = os.environ.get("QUEUE_NAME", "IttQueue-stage")
    DELAYED_QUEUE_NAME = os.environ.get("DELAYED_QUEUE_NAME", "IttDelayedQueue-stage")


HOST_URL = 'http://' + BUCKET_NAME + '.s3.amazonaws.com'


if not LOCAL:
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    MEDIA_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    AWS_STATIC_URL = 'http://' + AWS_STORAGE_BUCKET_NAME + '.s3.amazonaws.com/'
    STATIC_ROOT = STATIC_URL = AWS_STATIC_URL
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
