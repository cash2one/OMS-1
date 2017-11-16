from django.db import models
from .base import BaseModel

"""
逾期账单表
    -每个月最后一天凌晨0点结算
"""


class OverdueBill(BaseModel):

    amount = models.IntegerField(verbose_name='逾期费用')

    year = models.IntegerField(default=0, verbose_name='年份')

    month = models.IntegerField(default=0, verbose_name='月份')

    paid = models.NullBooleanField(verbose_name='是否支付')
    is_overdue = models.NullBooleanField(default=False, verbose_name='是否逾期')

    charge = models.ForeignKey('oms.Charge', null=True, verbose_name='支付凭证')

    paid_time = models.DateTimeField(null=True, verbose_name='支付完成时间')

    user_id = models.IntegerField(verbose_name='用户id')

    def __str__(self):
        return '''<OverdueBill({id})>:
            [amount({amount}),
            year({year}),
            user_id({user_id}),
            month({month})]'''.\
            format(id=self.id, amount=self.amount,
                   year=self.year,
                   user_id=self.user_id,
                   month=self.month)

    class Meta:
        ordering = ['-created_at']
        db_table = 'overdue_bill'
