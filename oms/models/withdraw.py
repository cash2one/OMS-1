from django.db import models
from .base import BaseModel


class Withdraw(BaseModel):

    withdraw_type = models.IntegerField(default=0, verbose_name='提现类型')
    transfer_id = models.CharField(max_length=50, verbose_name='ping++提现id')
    status = models.IntegerField(default=1, verbose_name='审核状态')
    status_info = models.CharField(default='未审核', max_length=50, verbose_name='审核状态')
    channel = models.CharField(max_length=50, verbose_name='渠道')
    order_no = models.CharField(max_length=50, verbose_name='内部订单号')
    amount = models.IntegerField(default=0, verbose_name='金额')

    app = models.CharField(max_length=50)
    _object = models.CharField(null=True, max_length=50)
    created = models.IntegerField(default=0, verbose_name='创建时间')
    amount_settle = models.IntegerField(default=0, verbose_name='金额')
    currency = models.CharField(default='cny', max_length=10, verbose_name='币种')
    livemode = models.NullBooleanField(default=False, verbose_name='线上模式')
    recipient = models.CharField(max_length=10, verbose_name='接受者id')
    description = models.CharField(null=True, max_length=300, verbose_name='备注')
    transaction_no = models.CharField(null=True, max_length=50, verbose_name='交易流水号')
    failure_msg = models.CharField(null=True, max_length=50, verbose_name='失败原因')
    extra = models.CharField(null=True, max_length=500, verbose_name='附带信息')
    _metadata = models.CharField(null=True, max_length=500, verbose_name='元数据')

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        db_table = 'withdraw'
