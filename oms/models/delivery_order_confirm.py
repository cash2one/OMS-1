# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class DeliveryOrderConfirm(BaseModel):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey('oms.Order')
    out_biz_code = models.\
        CharField(max_length=30, verbose_name='外部业务编码(消息ID;用于去重)')
    status = models.CharField(max_length=10, verbose_name='仓库确认的状态')
    confirm_type = models.\
        CharField(max_length=10, verbose_name='支持出库单多次发货')
    storageFee = models.FloatField(verbose_name='仓储费用')

    class Meta:
        ordering = ['-created_at']
        db_table = 'delivery_order_confirm'
