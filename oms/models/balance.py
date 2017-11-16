from django.db import models
from .base import BaseModel


"""
用户余额表(记录最终状态)
保证金的充值和提现，不在这里面体现
收入来源:
    1. 充值余额
    2. 预充值余额
    3. 单笔面单收入
    4. 仓主账单收入
支出去处：
    1. 账单支出
    2. 单笔面单支出
    3. 提现
"""


class Balance(BaseModel):

    amount = models.IntegerField(default=0, verbose_name='金额(单位分)')

    # 应该不需要货币种类
    # currency = models.CharField

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        db_table = 'balance'
