from django.db import models
from .base import BaseModel

"""
订单处理费用
"""


class OrderProcessFee(BaseModel):

    id = models.AutoField(primary_key=True)

    amount = models.IntegerField(default=0, verbose_name='订单处理费用')

    order = models.OneToOneField('oms.Order', verbose_name='关联订单')
    order_code = models.CharField(max_length=50, verbose_name='订单编号')

    sub_user_id = models.IntegerField(null=True, verbose_name='分仓用户id')
    share_user_id = models.IntegerField(null=True, verbose_name='共享仓用户id')

    warehouse_id = models.CharField(max_length=50, verbose_name='仓库id')
    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    def __str__(self):
        return '''<OrderProcessFee({id})>:
            [amount({amount}),
            user_id({user_id}),
            order_code({order_code}),
            warehouse_name({warehouse_name})]'''.\
            format(id=self.id, amount=self.amount,
                   share_user_id=self.share_user_id,
                   sub_user_id=self.sub_user_id,
                   order_code=self.order_code,
                   warehouse_name=self.warehouse_name)

    class Meta:
        ordering = ['-created_at']
        db_table = 'order_process_fee'
