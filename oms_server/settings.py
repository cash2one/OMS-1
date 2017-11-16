"""
Django settings for oms project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from . import logsettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qn!22(+g&w(5)u6_wqnpj+wmq82x38aiu-u@p69nl*bh$ow(xu'

OMS_APP_KEY = '23316736'
OMS_APP_SECRET = '123456'
COP_URL = 'http://192.168.1.101:8888'
OMS_CALLBACK_URL = 'oms_callback_url'

CMM = {
    "ip": "47.95.235.167",
    "port": 8002
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

TOKEN_KEY = 'xiaobm'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.


LOGGING = logsettings.get_logger_config(debug=DEBUG)

# memcached
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "KEY_FUNCTION": "utils.memcache.safe_key",
        "KEY_PREFIX": "memcached_default",
        "TIMEOUT": str(60 * 3),
        "LOCATION": [
            "localhost:11211"
        ],
    },
}

# Application definition
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'token',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'oms',
    'oms_server',
    'rest_framework'
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'oms_server.root_urls'


WSGI_APPLICATION = 'oms_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        # Or path to database file if using sqlite3.
        'NAME': 'oms',
        # Not used with sqlite3.
        'USER': 'youdan',
        # Not used with sqlite3.
        'PASSWORD': 'Cangmami2017',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': 'rm-2ze07ui3391359lojo.mysql.rds.aliyuncs.com',
        # Set to empty string for localhost. Not used with sqlite3.
        # 'HOST': '192.168.1.109',
        # Set to empty string for localhost. Not used with sqlite3.
        # 'HOST': '127.0.0.1',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '3306'
    }
}

# CELERY_RESULT_BACKEND = 'django-cache'
# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'oms_server.serializers.extension.custom_exception_handler'
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

LANGUAGES = (
    # ('en', 'English'),
    ('zh-cn', 'Simplified Chinese'),
)

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# CSRF_COOKIE_SECURE = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
