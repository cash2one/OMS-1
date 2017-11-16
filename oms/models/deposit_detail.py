from django.db import models
from .base import BaseModel


"""
保证金明细：
"""


class DepositDetail(BaseModel):

    STATEMENT_TYPE_CHOICES = (
        # 收入
        (1, '充值'),
        # 支出
        (2, '提现')
    )

    is_receipt = models.NullBooleanField(default=True, verbose_name='收入')

    amount = models.IntegerField(default=0, verbose_name='金额(单位分)')

    statement_type = models.IntegerField(choices=STATEMENT_TYPE_CHOICES,
                                         verbose_name='收支类型')

    # 关联信息

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        db_table = 'deposit_detail'
