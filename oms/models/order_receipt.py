from django.db import models
from .base import BaseModel

"""
共享仓用户订单收入概览
每处理一笔订单产生一笔收入
 - 快递费用
 - 处理费用
"""


class OrderReceipt(BaseModel):
    """
    amount = express_amount + order_process_amount
    """
    id = models.AutoField(primary_key=True)

    express_amount = models.IntegerField(default=0, verbose_name='快递费用')
    order_process_amount = models.IntegerField(default=0, verbose_name='处理费用')

    amount = models.IntegerField(default=0, verbose_name='订单账单总费用')

    # 一对一关联
    order = models.OneToOneField('oms.Order', verbose_name='关联订单')
    order_process_fee = models.OneToOneField('oms.OrderProcessFee',
                                             verbose_name='订单处理费')
    order_code = models.CharField(max_length=50, verbose_name='订单编号')

    user_id = models.IntegerField(verbose_name='共享仓用户id')

    warehouse_id = models.CharField(max_length=50, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_receipt'
