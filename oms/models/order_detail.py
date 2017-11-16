# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class OrderDetail(BaseModel):
    id = models.AutoField(primary_key=True)

    is_gift = models.NullBooleanField(default=False, verbose_name='是否是赠品')

    # 价格信息
    price = models.FloatField(default=0, verbose_name='实际价格')

    quantity = models.IntegerField(default=0, verbose_name='商品数量')

    total_price = models.FloatField(default=0, verbose_name='总价格')

    discount_price = models.FloatField(default=0, verbose_name='折扣价格')
    # 冗余信息
    # sku_tile = models.CharField(
    #     max_length=32,
    #     null=True,
    #     verbose_name='商品标题')

    sku_name = models.CharField(max_length=32, verbose_name='商品名称')

    item_code = models.CharField(max_length=64, verbose_name='商家编码')

    bar_code = models.CharField(max_length=64, verbose_name='商品条码')

    sku_spec = models.CharField(max_length=128, verbose_name='商品规格')

    locked_total_inventory = models.IntegerField(
        default=0,
        verbose_name='占用的总库存数目')

    locked_warehouse_inventory = models.IntegerField(
        default=0,
        verbose_name='占用的仓库库存数目')

    is_deliveryed = models.BooleanField(default=False, verbose_name='是否发货')

    locked_warehouse_id = models.CharField(
        max_length=30,
        default='0',
        verbose_name='分配的仓库')
    # 关联信息
    # sku_id = models.CharField(verbose_name='Sku标识')
    sku = models.ForeignKey('oms.Sku', null=True)
    order = models.ForeignKey(
        'oms.Order',
        related_name='order_detail',
        on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_detail'
