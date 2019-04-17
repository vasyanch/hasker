from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

if not DEBUG:
    STATIC_ROOT = '/home/django/www-data/hasker.com/static/'

