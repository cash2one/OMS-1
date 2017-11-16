# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class OrderExpress(BaseModel):

    id = models.AutoField(primary_key=True)
    delivery_order_confirm = models.\
        ForeignKey('oms.DeliveryOrderConfirm', null=True,)
    order = models.ForeignKey('oms.Order')
    express_code = models.CharField(
        max_length=32,
        null=True,
        verbose_name='快递编号'
    )
    logistics_name = models.\
        CharField(max_length=20, null=True, verbose_name='快递公司名称')
    logistics_code = models.\
        CharField(max_length=20, null=True, verbose_name='快递公司编码')
    length = models.FloatField(null=True, verbose_name='cm')
    width = models.FloatField(null=True, verbose_name='cm')
    height = models.FloatField(null=True, verbose_name='cm')
    theoretical_weight = models.FloatField(null=True, verbose_name='kg')
    weight = models.FloatField(null=True, verbose_name='kg')
    volume = models.FloatField(null=True, verbose_name='l')
    invoice_No = models.CharField(max_length=30, null=True, verbose_name='发票号')
    # TODO warehouse_id
    # warehouse_name

    # 发货省份
    # 收货省份

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_express'
