# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class SkuItemId(BaseModel):
    id = models.AutoField(primary_key=True)
    sku = models.ForeignKey('oms.Sku', null=False, verbose_name='关联的商品')
    warehouse_id = models.\
        CharField(max_length=20, null=False, verbose_name='同步的仓库')
    user_id = models.IntegerField(null=False, verbose_name='用户id')
    item_code = models.CharField(max_length=64, verbose_name='商家编码')

    item_id = models.CharField(max_length=64, verbose_name='仓库商品编码')

    class Meta:
        db_table = 'sku_item_id'
        unique_together = (('sku', 'warehouse_id'),)
