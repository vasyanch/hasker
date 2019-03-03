from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'NAME': 'hasker',
        'ENGINE': 'mysql.connector.django',
        'USER': 'django',
        'PASSWORD': 'wer789GHT15_',
        'OPTIONS': {
            'autocommit': True,
        }
    }
}

if not DEBUG:
    STATIC_ROOT = '/home/django/www-data/hasker.com/static/'
