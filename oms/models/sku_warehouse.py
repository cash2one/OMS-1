# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


# 库存中间表：多对多
class SkuWarehouse(BaseModel):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(default=0, verbose_name='Sku库存数量')

    available_quantity = models.IntegerField(default=0, verbose_name='可用Sku库存数量')

    warehouse_id = models.\
        CharField(max_length=20, null=False, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=32, verbose_name='仓库名称')

    warehouse_province = models.CharField(max_length=32, null=True, verbose_name='仓库省份')

    warehouse_city = models.CharField(max_length=32, null=True, verbose_name='仓库城市')

    warehouse_area = models.CharField(max_length=32, null=True, verbose_name='仓库地区')

    warehouse_detail = models.CharField(max_length=32, null=True, verbose_name='仓库详细地址')

    warehouse_longitude = models.CharField(max_length=32, null=True, verbose_name='仓库经度')

    warehouse_latitude = models.CharField(max_length=32, null=True, verbose_name='仓库纬度')

    sku = models.ForeignKey('oms.Sku', on_delete=models.CASCADE, verbose_name='Sku')

    user_id = models.IntegerField(null=False, verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        app_label = 'oms'

    @property
    def warehouse_address(self):
        return self.warehouse_province + self.warehouse_city +\
            self.warehouse_area + self.warehouse_detail

    def __str__(self):
        return '仓库-sku'
