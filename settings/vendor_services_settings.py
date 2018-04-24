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

# Memcached Cloud settings
# https://devcenter.heroku.com/articles/memcachedcloud
def get_cache():
  import os
  try:
    servers = os.environ['MEMCACHEDCLOUD_SERVERS']
    username = os.environ['MEMCACHEDCLOUD_USERNAME']
    password = os.environ['MEMCACHEDCLOUD_PASSWORD']
    return {
        'default': {
            'BACKEND': 'django_bmemcached.memcached.BMemcached',
            'LOCATION': servers.split(','),
            'OPTIONS': {
                'username': username,
                'password': password,
            }
        }
    }
  except:
    return {
      'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
    }

CACHES = get_cache()

# UpdateCacheMiddleware settings. For auto caching RESTful API.
CACHE_MIDDLEWARE_SECONDS = 60 * 60 # cache pages for 60 min same as SHORT period in price model
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_KEY_PREFIX = ''

# Temporary disable cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Celery settings (optimized for CloudAMQP)
CELERY_BROKER_URL =  os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost//')
# CELERY_BROKER_POOL_LIMIT = 1 # for free tier of the ampq https://devcenter.heroku.com/articles/cloudamqp#celery
# CELERYD_TASK_TIME_LIMIT = 2*60*60 # 2 hours, in seconds
# CELERY_BROKER_HEARTBEAT = None # CloudAMQP using TCP keep-alive instead
# CELERY_BROKER_CONNECTION_TIMEOUT = 30 # default 4 is not enough for CloudAMQP
# CELERY_TASK_PUBLISH_RETRY = False # Do not retry tasks in the case of connection loss
# CELERYD_PREFETCH_MULTIPLIER = 1 # Disable prefetching
# CELERY_ACKS_LATE = True # Task will be acknowledged after the task has been executed, not just before (the default behavior)


# Telegram settings for itt-info-bot
INFO_BOT_TELEGRAM_BOT_API_TOKEN = os.environ.get('INFO_BOT_TELEGRAM_BOT_API_TOKEN', '123ABC')
INFO_BOT_CACHE_TELEGRAM_BOT_SECONDS = 4 * 60 * 60 # cache telegram bot reply for 4 hour
INFO_BOT_CRYPTOPANIC_API_TOKEN = os.environ.get('INFO_BOT_CRYPTOPANIC_API_TOKEN', '123ABC')

INCOMING_SQS_QUEUE = os.environ.get('INCOMING_SQS_QUEUE')
SNS_SIGNALS_TOPIC_ARN = os.environ.get('SNS_SIGNALS_TOPIC_ARN', None)