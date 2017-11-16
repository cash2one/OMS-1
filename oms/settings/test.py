# -*- coding:utf-8 -*-
from .base import *

SECRET_KEY = 'qn!22(+g&w(5)u6_wqnpj+wmq82x38aiu-u@p69nl*bh$ow(xu'
DEVELOPER_OAUTH_PAY_AMOUNT = 30000
DEBUG = True
CMM_URL = 'http://test.api.xbmhz.com'
# GET_USER_INFO =\
#     'http://test.open.api.aircos.com/api/users/show'
COP_URL = 'http://test.api.cop.aircos.com/api/'
OMS_CALLBACK_URL = 'http://test.api.oms.aircos.com/api/cop/'

GET_USER_INFO_URL = 'http://test.api.xbmhz.com/api/users/'
GET_ALL_SUB_USERS =\
    'http://test.api.xbmhz.com/api/users/all_sub_users'
GET_WAREHOUSE_BY_ID_URL =\
    'http://test.api.xbmhz.com/api/users/warehouses/'
GET_WAREHOUSE_BY_CODE_URL =\
    'http://test.api.xbmhz.com/api/warehouses/warehouse_info'
LIST_AVAILABLIE_WAREHOUSE_URL =\
    'http://test.api.xbmhz.com/api/users/available_warehouses'
LIST_OWN_WAREHOUSE_URL =\
    'http://test.api.xbmhz.com/api/users/own_warehoues'
GET_ALL_USER_WAREHOUSES =\
    'http://test.api.xbmhz.com/api/users/user_warehouses'

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oms',
        'USER': 'youdan',
        'PASSWORD': 'Cangmami2017',
        'HOST': 'rm-2ze07ui3391359lojo.mysql.rds.aliyuncs.com',
        'PORT': '3306',
    }
}
PINGXX_APPSECRET = 'sk_test_ufXD0OSW9CGOCW1abDPuTCOS'
