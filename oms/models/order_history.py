# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


class OrderHistory(BaseModel):

    id = models.AutoField(primary_key=True)
    order = models.ForeignKey('oms.order', null=False, verbose_name='订单')
    is_system = models.BooleanField(null=False, verbose_name='是否系统自动处理')
    operator = models.CharField(max_length=30, null=False, verbose_name='操作员id')
    account = models.CharField(max_length=50, verbose_name='操作员账号')
    action = models.CharField(max_length=10, null=False, verbose_name='操作动作')
    comment = models.CharField(max_length=100, verbose_name='备注')

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_history'
