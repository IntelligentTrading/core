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

# Heroku Memcachier settings
# Add MemCachier addon to heroku
# def get_cache():
#   import os
#   try:
#     servers = os.environ['MEMCACHIER_SERVERS']
#     username = os.environ['MEMCACHIER_USERNAME']
#     password = os.environ['MEMCACHIER_PASSWORD']
#     return {
#       'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#         # TIMEOUT is not the connection timeout! It's the default expiration
#         # timeout that should be applied to keys! Setting it to `None`
#         # disables expiration.
#         'TIMEOUT': None,
#         'LOCATION': servers,
#         'OPTIONS': {
#           'binary': True,
#           'username': username,
#           'password': password,
#           'behaviors': {
#             # Enable faster IO
#             'no_block': True,
#             'tcp_nodelay': True,
#             # Keep connection alive
#             'tcp_keepalive': True,
#             # Timeout settings
#             'connect_timeout': 2000, # ms
#             'send_timeout': 750 * 1000, # us
#             'receive_timeout': 750 * 1000, # us
#             '_poll_timeout': 2000, # ms
#             # Better failover
#             'ketama': True,
#             'remove_failed': 1,
#             'retry_timeout': 2,
#             'dead_timeout': 30,
#           }
#         }
#       }
#     }
#   except:
#     return {
#       'default': {
#         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
#       }
#     }


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

