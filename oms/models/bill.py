from django.db import models
from .base import BaseModel

"""
账单表
bill_type(过程产生):
    1. 仓储费
    2. 快递面单费(是不是要分成两单)
    3. 订单处理费
    4. 逾期费(目前没有) (其实就是上个月产生的未结算账单)
汇总查询(根据仓库查看详情)：
    1. 待支付账单
    2. 总账单
    3. 已支付账单
问题：
    和订单需要关联吗？
    快递费用是不是拆成两单(一笔未支付、一笔已支付)
    前端根据仓库支付，后台怎么处理
"""


# 一笔账单(作废)
class Bill(BaseModel):

    BILL_TYPE_CHOICES = (
        (1, '仓储费用'),
        (2, '快递费用'),
        (3, '订单处理费用'),
        (4, '快递面单费用')
    )

    bill_type = models.IntegerField(choices=BILL_TYPE_CHOICES,
                                    verbose_name='账单费用类型')

    # 费用
    storge_amount = models.IntegerField(verbose_name='仓储费用')
    express_amount = models.IntegerField(verbose_name='快递费用')
    order_process_amount = models.IntegerField(verbose_name='订单处理费用')
    express_sheet_amount = models.IntegerField(verbose_name='面单费用')

    amount = models.IntegerField(verbose_name='总金额(单位分)')

    # 已支付 和 未支付 面单费用怎么处理？
    # 就两种状态，还是有支付中，未到账
    paid = models.NullBooleanField(default=False, verbose_name='是否支付')
    express_sheet_paid = models.NullBooleanField(default=False,
                                                 verbose_name='面单是否支付')

    warehouse_id = models.CharField(max_length=20, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    order_id = models.ForeignKey('oms.Order', verbose_name='关联订单')

    user_id = models.IntegerField(verbose_name='用户id')

    class Meta:
        ordering = ['-created_at']
        db_table = 'bill'
