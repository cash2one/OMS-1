# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class OrderExpressItem(BaseModel):
    id = models.AutoField(primary_key=True)
    delivery_order_confirm = models.ForeignKey('oms.DeliveryOrderConfirm')
    order = models.ForeignKey('oms.Order')
    item_code = models.CharField(max_length=30, verbose_name='商品商家编码')
    item_id = models.CharField(max_length=30, verbose_name='仓库编码')
    quantity = models.IntegerField(verbose_name='发货数量')

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_express_item'
