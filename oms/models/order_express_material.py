# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class OrderExpressMaterial(BaseModel):
    id = models.AutoField(primary_key=True)
    order_express = models.ForeignKey('oms.OrderExpress')
    order = models.ForeignKey('oms.Order', verbose_name='订单')
    meterial_type = models.CharField(max_length=10, verbose_name='耗材类型')
    quantity = models.IntegerField(verbose_name='数量')

    class Meta:
        db_table = 'order_express_meteria'
