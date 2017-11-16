from django.db import models
from .base import BaseModel

"""
仓储账单
"""


# 每天凌晨根据，应该根据当前库存(结算的是第二天的仓储费用)生成一笔账单
class StorgeBill(BaseModel):

    id = models.AutoField(primary_key=True)

    amount = models.IntegerField(verbose_name='总金额(单位分)')
    volume = models.FloatField(default=0.0, verbose_name='商品体积')

    paid = models.NullBooleanField(default=False, verbose_name='是否支付')
    charge = models.ForeignKey('oms.Charge', null=True, verbose_name='支付凭证')
    paid_time = models.DateTimeField(null=True, verbose_name='支付完成时间')
    is_overdue = models.NullBooleanField(default=False, verbose_name='是否逾期')

    warehouse_id = models.CharField(max_length=20, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    user_id = models.IntegerField(verbose_name='用户id')

    charge = models.ForeignKey('oms.Charge', null=True, verbose_name='支付凭证')

    storge_fee = models.ForeignKey('oms.StorgeFee', verbose_name='存储费用')

    def __str__(self):
        return '''<StorgeBill({id})>:[amount({amount}),volume({volume}),user_id({user_id}),warehouse_name({warehouse_name})]'''.\
            format(id=self.id, amount=self.amount,
                   volume=self.volume,
                   user_id=self.user_id,
                   warehouse_name=self.warehouse_name)

    class Meta:
        db_table = 'storge_bill'
