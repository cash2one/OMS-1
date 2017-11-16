from django.db import models
from .base import BaseModel

"""
预充值余额表
"""


class PrePaidBalance(BaseModel):

    amount = models.IntegerField(verbose_name='金额(单位分)')

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        db_table = 'prepaid_balance'