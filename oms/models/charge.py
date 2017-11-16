from django.db import models
from .base import BaseModel

"""
用户充值表
只是一个记录流程，状态
当charge状态为paid时，需要改变相应的数据，例如余额、保证金、预充值费用
charge_type:
    1. 充值
    2. 预充值
    3. 保证金支付
"""


class Charge(BaseModel):

    PAY_TYPE_CHOICE = (
        (1, '充值'),
        (2, '账单支付'),
        (3, '保证金支付')
    )

    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    pay_type = models.IntegerField(default=1, choices=PAY_TYPE_CHOICE,
                                   verbose_name='支付类型')
    charge_id = models.CharField(max_length=50, verbose_name='ping++支付id')

    client_ip = models.CharField(max_length=50, verbose_name='客户端ip')
    created = models.IntegerField(verbose_name='支付创建的时间timestamp')

    paid = models.NullBooleanField(default=False, verbose_name='是否支付')
    refunded = models.NullBooleanField(default=False,
                                       verbose_name='是否存在退款，无论成功失败与否')

    channel = models.CharField(max_length=20, verbose_name='支付渠道')
    order_no = models.CharField(max_length=50, verbose_name='商户订单号')

    amount = models.IntegerField(verbose_name='支付金额(单位分)')
    amount_settle = models.IntegerField(default=0, verbose_name='清算金额(单位分)')
    currency = models.CharField(default='cny', max_length=10, verbose_name='货币代码(人民币为cny)')

    time_paid = models.IntegerField(null=True, verbose_name='支付完成的时间timestamp')
    transaction_no = models.CharField(null=True, max_length=50, verbose_name='交易流水号')

    failure_code = models.CharField(null=True, max_length=50, verbose_name='错误码')
    failure_msg = models.CharField(null=True, max_length=50, verbose_name='错误消息描述')
    credential = models.CharField(null=True, max_length=1000, verbose_name='支付凭证')
    description = models.CharField(null=True, max_length=50, verbose_name='订单附加说明')

    credential = models.CharField(max_length=500, verbose_name='支付凭证')

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        db_table = 'charge'
