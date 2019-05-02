from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD_FOR_HASKER')

DATABASES = {
    'default': {
        'NAME': 'hasker',
        'ENGINE': 'mysql.connector.django',  # 'django.db.backends.mysql'
        'USER': 'django',
        'PASSWORD': MYSQL_PASSWORD,
        'OPTIONS': {
            'autocommit': True,
        },
    }
}

if not DEBUG:
    STATIC_ROOT = '/home/django/www-data/hasker/static/'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'vasyanch@yandex.ru'
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = 'vasyanch@yandex.ru'
EMAIL_USE_SSL = True

SERVER_EMAIL = EMAIL_HOST_USER
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
