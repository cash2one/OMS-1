# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class StockInDetail(BaseModel):
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField(null=False, verbose_name='sku数量')

    # 冗余信息
    sku_name = models.CharField(max_length=128, verbose_name='商品名称')

    sku_spec = models.CharField(max_length=128, verbose_name='商品规格')

    # user_code = models.CharField(max_length=64, verbose_name='商家编码(废弃)')

    item_code = models.CharField(max_length=64, verbose_name='商家编码')

    item_id = models.CharField(max_length=64, verbose_name='仓库商品编码')

    bar_code = models.CharField(max_length=64, verbose_name='商品条码')

    sku = models.ForeignKey('oms.Sku', null=False, verbose_name='关联的商品')

    user_id = models.IntegerField(null=False, verbose_name='用户id')

    stock_in = models.\
        ForeignKey('oms.StockIn', null=False, verbose_name='关联入库单')

    class Meta:
        db_table = 'stock_in_detail'
