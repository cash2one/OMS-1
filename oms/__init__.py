# -*- coding: utf-8 -*-
import pymysql
# 引入celery实例对象
from .custom_celery import app as celery_app
pymysql.install_as_MySQLdb()
