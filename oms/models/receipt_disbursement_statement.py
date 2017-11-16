from django.db import models
from .base import BaseModel


"""
收支明细表(过程产生)：
"""


class ReceiptDisbursementStatement(BaseModel):

    STATEMENT_TYPE_CHOICES = (
        # 收入
        (1, '充值'),
        (2, '预充值'),
        (3, '保证金'),
        (4, '面单费用收入'),
        (5, '账单收入'),
        # 支出
        (11, '账单支出'),
        (12, '面单费用支出'),
        (12, '提现')
    )

    is_receipt = models.NullBooleanField(default=True, verbose_name='收入')

    amount = models.IntegerField(default=0, verbose_name='金额(单位分)')

    statement_type = models.IntegerField(choices=STATEMENT_TYPE_CHOICES,
                                         verbose_name='收支类型')

    # 关联信息
    # charge_id = models.ForeignKey('oms.Charge',null=True, verbose_name='支付id')
    # storge_bill = models.ForeignKey('oms.StorgeBill', null=True, verbose_name='仓储账单')
    # order_bill = models.ForeignKey('oms.OrderBill', null=True, verbose_name='订单账单')

    user_id = models.IntegerField(verbose_name='用户id')

    def __str__(self):
        money = int(self.amount) if self.is_receipt else -int(self.amount)
        return '''<ReceiptDisbursementStatement({id})>:[amount({amount}),user_id({user_id})]'''.\
            format(id=self.id, amount=money,
                   user_id=self.user_id)

    class Meta:
        ordering = ['-created_at']
        db_table = 'deceipt_disbursement_statement'
