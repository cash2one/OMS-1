# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


"""
当应用类型为ISV时，需要用到此表
即使是自有应用，有一些平台比如youzan，也是需要此表提供"kdt_id"。在此表中，就是auth_store_id字段。
当为自有应用时，授权商铺id就是自己的商铺id

"""


class Token(BaseModel):
    id = models.AutoField(primary_key=True)
    auth_store_id = models.\
        CharField(max_length=40, blank=True, verbose_name='授权商铺的id')

    plat = models.ForeignKey('oms.Plat')
    app_key = models.CharField(max_length=80)
    app_secret = models.CharField(max_length=512)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512)
    expire_in = models.IntegerField(default=0, null=True)
    expire_time = models.IntegerField(default=0, null=True)

    class Meta:
        app_label = 'oms'
        abstract = False

    def __str__(self):
        return self.name
