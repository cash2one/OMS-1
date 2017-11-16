# -*- coding: UTF-8 -*-
from django.db import models
from oms.models.base import BaseModel
# from oms.models.order import Order
import uuid


class SplitCombineOrder(BaseModel):
    id = models.AutoField(primary_key=True)
    # origin_order = models.ForeignKey('oms.Order')
    # origin_order = models.UUIDField()
    sub_order_sequence = models.IntegerField(default=0, null=True)
    new_order = models.CharField(max_length=30, blank=False)
    original_order = models.CharField(max_length=30, blank=False)
    # 该订单是否合并，如果合并，查找合并订单
    is_combined = models.BooleanField(default=False)
    # 该订单是否拆单，如果拆单，查找SplitOrder
    is_splited = models.BooleanField(default=False)

    def __str__(self):
        return str(self.new_order) + ' of ' + str(self.original_order)
