from django.db import models
from .base import BaseModel

"""
订单处理收入表
"""


# 订单处理单价
class OrderProcessReceipt(BaseModel):

    amount = models.IntegerField(verbose_name='订单处理费用')

    order = models.ForeignKey('oms.Order', verbose_name='关联订单')

    order_code = models.CharField(max_length=50, verbose_name='订单编号')

    user_id = models.IntegerField(verbose_name='共享仓用户id')

    warehouse_id = models.CharField(verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    def __str__(self):
        return '''<OverdueBill({id})>:
            [amount({amount}),
            user_id({user_id}),
            order_code({order_code}),
            warehouse_name({warehouse_name})]'''.\
            format(id=self.id, amount=self.amount,
                   user_id=self.user_id,
                   order_code=self.order_code,
                   warehouse_name=self.warehouse_name)

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_express_receipt'