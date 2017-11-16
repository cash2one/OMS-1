# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class Consignee(BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='收货人姓名')
    country = models.CharField(max_length=20, verbose_name='收货人国籍')
    province = models.CharField(max_length=32, verbose_name='收货人省份')
    city = models.CharField(max_length=32, verbose_name='收货城市')
    area = models.CharField(max_length=32, verbose_name='收货区域')
    detail = models.CharField(max_length=32, verbose_name='收货详细地址')
    zip = models.CharField(max_length=10, verbose_name='收货人邮编')
    town = models.CharField(max_length=32, verbose_name='收货人街道地址')
    phone = models.CharField(max_length=22, verbose_name='收货人电话')

    class Meta:
        ordering = ['-created_at']
        abstract = False
        db_table = 'consignee'
