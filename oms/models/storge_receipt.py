from django.db import models
from .base import BaseModel

"""
共享仓用户存储收入
"""


class StorgeReceipt(BaseModel):

    id = models.AutoField(primary_key=True)

    amount = models.IntegerField(verbose_name='总金额(单位分)')

    warehouse_id = models.CharField(max_length=20, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    user_id = models.IntegerField(verbose_name='共享仓用户id')

    storge_fee = models.ForeignKey('oms.StorgeFee', verbose_name='存储费用')

    def __str__(self):
        return '''<StorgeReceipt({id})>:[amount({amount}),user_id({user_id}),warehouse_name({warehouse_name})]'''.\
            format(id=self.id, amount=self.amount,
                   user_id=self.user_id,
                   warehouse_name=self.warehouse_name)

    class Meta:
        ordering = ['-created_at']
        db_table = 'storge_receipt'
