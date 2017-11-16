from django.db import models
from .base import BaseModel

"""
快递费用
"""


class OrderExpressFee(BaseModel):

    id = models.AutoField(primary_key=True)

    package_weight = models.FloatField(default=0.0, verbose_name='包裹重量')

    amount = models.IntegerField(default=0, verbose_name='金额(单位分)')

    sheet_amount = models.IntegerField(default=0, verbose_name='面单费用')

    order = models.ForeignKey('oms.Order', verbose_name='关联订单')
    order_code = models.CharField(max_length=50, verbose_name='订单编号')
    order_express = models.ForeignKey('oms.OrderExpress',
                                      verbose_name='订单快递')

    warehouse_id = models.CharField(max_length=50, verbose_name='仓库id')
    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    sub_user_id = models.IntegerField(null=True, verbose_name='分仓用户id')
    share_user_id = models.IntegerField(null=True, verbose_name='共享仓用户id')

    order_bill_overview = models.ForeignKey('oms.OrderBill',
                                            null=True,
                                            verbose_name='分仓用户订单账单')

    order_receipt_overview = models.ForeignKey('oms.OrderReceipt',
                                               null=True,
                                               verbose_name='共享仓用户订单收入')

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_express_fee'
