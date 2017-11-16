from django.db import models
from .base import BaseModel

"""
用仓用户订单账单概览
每处理一笔订单产生一笔账单
 - 快递费用(包含面单费用)
 - 处理费用
"""


class OrderBill(BaseModel):
    """
    amount = express_amount + order_process_amount
    paid = False:
        unsettle_amount = amount - express_sheet_amount
        settle_amount = express_sheet_amount
    paid = True:
        unsettle_amount = 0
        settle_amount = amount
    """
    id = models.AutoField(primary_key=True)

    express_amount = models.IntegerField(default=0, verbose_name='快递费用')
    express_sheet_amount = models.IntegerField(default=0, verbose_name='面单费用')
    order_process_amount = models.IntegerField(default=0, verbose_name='处理费用')

    unsettle_amount = models.IntegerField(default=0, verbose_name='未结算费用')
    amount = models.IntegerField(default=0, verbose_name='订单账单总费用')

    charge = models.ForeignKey('oms.Charge', null=True, verbose_name='支付凭证')
    paid = models.NullBooleanField(default=False, verbose_name='是否支付')
    paid_time = models.DateTimeField(null=True, verbose_name='支付完成时间')
    is_overdue = models.NullBooleanField(default=False, verbose_name='是否逾期')

    # 一对一关联
    order = models.OneToOneField('oms.Order', verbose_name='关联订单')
    order_process_fee = models.OneToOneField('oms.OrderProcessFee',
                                             verbose_name='订单处理费')
    order_code = models.CharField(max_length=50, verbose_name='订单编号')

    user_id = models.IntegerField(verbose_name='用仓用户id')

    warehouse_id = models.CharField(max_length=50, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')
    
    def __str__(self):
        return '''<OrderBill({id})>:
            [express_amount({express_amount}),
            express_sheet_amount({express_sheet_amount}),
            process_amount({process_amount}),
            order_code({order_code}),
            user_id({user_id}),
            warehouse_name({warehouse_name})]'''.\
            format(id=self.id, express_amount=self.express_amount,
                   express_sheet_amount=self.express_sheet_amount,
                   process_amount=self.order_process_amount,
                   order_code=self.order_code,
                   user_id=self.user_id,
                   warehouse_name=self.warehouse_name)

    class Meta:
        db_table = 'order_bill'