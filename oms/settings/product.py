# -*- coding:utf-8 -*-

from .base import *



DEVELOPER_OAUTH_PAY_AMOUNT = 30000
DEBUG = False

CMM_URL = 'http://api.xbmhz.com'
# GET_USER_INFO =\
#     'http://api.open.aircos.com/api/users/show'
# COP_URL = 'http://47.95.235.167:8001/api/'
COP_URL = 'http://api.cop.aircos.com/api/'
OMS_CALLBACK_URL = 'http://api.oms.aircos.com/api/cop/'


GET_USER_INFO_URL = 'http://api.xbmhz.com/api/users/'
GET_ALL_SUB_USERS =\
    'http://api.xbmhz.com/api/users/all_sub_users'
GET_WAREHOUSE_BY_ID_URL =\
    'http://api.xbmhz.com/api/users/warehouses/'
GET_WAREHOUSE_BY_CODE_URL =\
    'http://api.xbmhz.com/api/warehouses/warehouse_info'
LIST_AVAILABLIE_WAREHOUSE_URL =\
    'http://api.xbmhz.com/api/users/available_warehouses'
LIST_OWN_WAREHOUSE_URL =\
    'http://api.xbmhz.com/api/users/own_warehoues'
GET_ALL_USER_WAREHOUSES =\
    'http://api.xbmhz.com/api/users/user_warehouses'

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oms',
        'USER': 'aircos',
        'PASSWORD': 'Aircos201710',
        'HOST': 'rm-2ze2id33njw5c9414.mysql.rds.aliyuncs.com',
        'PORT': '3306',
    }
}
PINGXX_APPSECRET = 'sk_live_8OuHePy9W98Kn9CmzPibXHCO'
