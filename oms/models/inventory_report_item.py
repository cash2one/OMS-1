from django.db import models
from .base import BaseModel


class InventoryReportItem(BaseModel):

    INVENTORY_TYPE = (
        ('ZP', '正品'),
        ('CC', '残次'),
        ('JS', '机损'),
        ('XS', '箱损'),
        ('ZT', '在途库存'),
    )

    id = models.AutoField(primary_key=True)
    inventory_report = models.ForeignKey(
        'oms.InventoryReport',
        verbose_name='盘点报告')

    item_code = models.CharField(max_length=30, verbose_name='商家编码')
    item_id = models.CharField(max_length=30, verbose_name='仓储系统商品ID')
    # inventoryType 库存类型(ZP=正品;CC=残次;JS=机损;XS= 箱损;ZT=在途库存;默认为ZP)
    inventory_type = models.CharField(
        max_length=10,
        choices=INVENTORY_TYPE,
        verbose_name='库存类型')
    # quantity 盘盈盘亏商品变化量(盘盈为正数;盘亏为负数)
    quantity = models.IntegerField(
        verbose_name='盘盈盘亏商品变化量(盘盈为正数;盘亏为负数)')
    # totalQty 库存商品总量
    total_qty = models.IntegerField(
        null=True,
        verbose_name='库存商品总量(可选)')
    # batchCode 批次编码
    batch_code = models.CharField(null=True, max_length=30, verbose_name='批次编码')
    # productDate 商品生产日期(YYYY-MM-DD)
    product_date = models.DateTimeField(null=True, verbose_name='商品生产日期(YYYY-MM-DD)')
    # expireDate 商品过期日期(YYYY-MM-DD)
    expire_date = models.DateTimeField(null=True, verbose_name='商品过期日期(YYYY-MM-DD)')
    # produceCode P1234生产批号
    produce_code = models.CharField(max_length=30, null=True, verbose_name='生产批号')
    # snCode 商品序列号
    sn_code = models.CharField(max_length=30, null=True, verbose_name='商品序列号')
    # remark 备注
    remark = models.CharField(max_length=50, null=True, verbose_name='备注')

    class Meta:
        ordering = ['-created_at']
        db_table = 'inventory_report_item'
