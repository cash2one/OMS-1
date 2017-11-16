from django.db import models
from .base import BaseModel

"""
共享仓用户快递收入表
"""


class ExpressReceipt(BaseModel):

    id = models.AutoField(primary_key=True)

    amount = models.IntegerField(default=0.0, verbose_name='金额(单位分)')

    delivery_order_code = models.CharField(max_length=50, verbose_name='出库单号')

    order_id = models.IntegerField(verbose_name='订单id')
    order_code = models.CharField(max_length=50, verbose_name='订单编号')

    order_express = models.ForeignKey('oms.OrderExpress', max_length=50,
                                      verbose_name='订单快递')

    user_id = models.IntegerField(verbose_name='共享仓用户id')

    warehouse_id = models.CharField(verbose_name='仓库id')
    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')
    warehouse_code = models.CharField(verbose_name='仓库code')

    order_bill_overview = models.ForeignKey('oms.OrderBillOverview',
                                            verbose_name='订单账单概览')

    class Meta:
        ordering = ['-created_at']
        db_table = 'express_sheet_bill'