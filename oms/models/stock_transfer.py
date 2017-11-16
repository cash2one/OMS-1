# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


# 库存调拨单
class StockTransfer(BaseModel):

    STOCK_TRANSFER_STATUS = (
        (1, '调拨中'),
        (2, '入仓审核'),
        (3, '完成'),
        (4, '取消')
    )
    id = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name='调拨单号',
        editable=False)

    stock_transfer_status = models.IntegerField(
        default=1,
        null=False,
        choices=STOCK_TRANSFER_STATUS,
        verbose_name='调拨状态')

    stock_transfer_code = models.CharField(
        max_length=32,
        null=False,
        verbose_name='调拨单编号')

    express = models.CharField(
        max_length=32,
        null=False,
        verbose_name='快递公司')

    express_number = models.CharField(
        max_length=300,
        null=False,
        verbose_name='快递单号')

    warehouse_out_id = models.CharField(
        max_length=20,
        null=False,
        verbose_name='调出仓库id')
    warehouse_in_id = models.CharField(
        max_length=20,
        null=False,
        verbose_name='调入仓库id')
    user_id = models.IntegerField(null=False, verbose_name='用户id')

    class Meta:
        app_label = 'oms'
        db_table = 'stock_transfer'
