# -*- coding: UTF-8 -*-
import os
import socket
import datetime
from celery.schedules import crontab
# 单独的配置文件
# 写上自己的hostname， 配置相应项
# if socket.gethostname() in ['syntactic-sugardeMacBook-Pro.local']:
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'oms',
#             'USER': 'root',
#             'PASSWORD': 'root',
#             'HOST': '127.0.0.1',
#             'PORT': '3306'
#         }
#     }
# elif socket.gethostname() == "DESKTOP-F12BPAF":
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'oms',
#             'USER': 'root',
#             'PASSWORD': '123456',
#             'HOST': '127.0.0.1',
#             'PORT': '3306'
#         }
#     }
# else:
#     # 服务器数据库配置， Don't touch it!
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'oms',
#             'USER': 'youdan',
#             'PASSWORD': 'Cangmami2017',
#             'HOST': 'rm-2ze07ui3391359lojo.mysql.rds.aliyuncs.com',
#             'PORT': '3306'
#         }
#     }

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 开放平台对接配置
OMS_APP_KEY = '23316736'
OMS_APP_SECRET = '123456'
# COP_URL = 'http://47.95.235.167:8001/api/'
# OMS_CALLBACK_URL = 'http://47.95.235.167:8000/api/cop/'


# celery配置
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['application/json', ]
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'

# CELERY_ENABLE_UTC = False
CELERYBEAT_SCHEDULE = {
    # 'storge_billing_every_day_0_hour': {
    #     'task': 'oms_server.tasks.storge_billing',
    #     'schedule': crontab(minute='0', hour='16'),
    #     'args': ()
    # },
    # 'overdue_billing_every_month_first_day': {
    #     'task': 'oms_server.tasks.overdue_billing',
    #     'schedule': crontab(minute='0', hour='0', day_of_month='1'),
    #     'args': ()
    # },
    'refresh_token_every_day_2_hour': {
        'task': 'oms_server.tasks.refresh_token',
        'schedule': crontab(minute='0', hour='18'),     # UTC时间
        'args': ()
    },
}

SECRET_KEY = 'qn!22(+g&w(5)u6_wqnpj+wmq82x38aiu-u@p69nl*bh$ow(xu'

# token生成密钥
TOKEN_KEY = 'xiaobanma2017'
TOKEN_EXPIRE_TIME = 432000

# ping++密钥
PINGXX_APPID = 'app_Cer1KKCOO4y5CK8y'

# 面单费
EXPRESS_SHEET_COST = 200

# taobao.qimen  aircos.cop
# METHOD_PRE = 'taobao.qimen.'
METHOD_PRE = 'aircos.cop.'

# DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        "simple": {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'propagate': True,
        #     'level': 'DEBUG',
        # },
        'custom': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

# 允许跨域
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

# 安装的app
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'oms',
    'oms_api',
    'oms_server',
    'django_celery_beat',
    'django_celery_results',
    'rest_framework'
)

# 中间件
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
    'oms.extension.request_middleware.RequestMiddleware'
)

# 模板(正式环境去掉)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# rest_framework提供异常处理机制
REST_FRAMEWORK = {
    'EXCEPTION_HANDLER':
    'oms.extension.response_wrapper.custom_exception_handler'
}

# url配置
ROOT_URLCONF = 'oms.urls'

# wsgi配置
WSGI_APPLICATION = 'oms.wsgi.application'


# 语言时区配置
LANGUAGE_CODE = 'zh-Hans'

LANGUAGES = (
    ('zh-cn', 'Simplified Chinese'),
)

TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False

USE_I18N = False

USE_L10N = False


STATIC_URL = '/static/'
