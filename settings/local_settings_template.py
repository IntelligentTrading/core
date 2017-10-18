SECRET_KEY = ''

# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql_psycopg2',
        'NAME':     '',
        'USER':     '',
        'PASSWORD': '',
        'HOST':     'localhost',
        'PORT':     '5432',
    }
}


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

AWS_OPTIONS = {
    'AWS_ACCESS_KEY_ID' : '',
    'AWS_SECRET_ACCESS_KEY' : '',
    'AWS_STORAGE_BUCKET_NAME' : 'itt-stage',
}


#MEMCACHED CLOUD RESPONSE CACHEING
#no cacheing on local dev
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
