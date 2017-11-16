from django.db import models
from .base import BaseModel

"""
保证金表(最终呈现状态)
"""


class Deposit(BaseModel):

    amount = models.IntegerField(default=0, verbose_name='金额(单位分)')

    # 信息冗余，当用户信息修改是需要修改
    # user_phone
    user_name = models.CharField(max_length=50, verbose_name='用户名称')

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        db_table = 'deposit'
