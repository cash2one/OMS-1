from django.db import models
from .base import BaseModel


class StockchangeReport(BaseModel):

    INVENTORY_TYPE = (
        ('ZP', '正品'),
        ('CC', '残次'),
        ('JS', '机损'),
        ('XS', '箱损'),
        ('ZT', '在途库存'),
    )
    ORDER_TYPE = (
        ('JYCK', '一般交易出库单'),  # JYCK=一般交易出库单;
        ('HHCK', '换货出库'),  # HHCK=换货出库;
        ('BFCK', '补发出库'),  # BFCK=补发出库;
        ('PTCK', '普通出库单'),  # PTCK=普通出库单;
        ('DBCK', '调拨出库'),  # DBCK=调拨出库;
        ('B2BRK', 'B2B入库'),  # B2BRK=B2B入库;
        ('B2BCK', 'B2B出库'),  # B2BCK=B2B出库;
        ('QTCK', '其他出库'),  # QTCK=其他出库;
        ('SCRK', '生产入库'),  # SCRK=生产入库;
        ('LYRK', '领用入库'),  # LYRK=领用入库;
        ('CCRK', '残次品入库'),  # CCRK=残次品入库;
        ('CGRK', '采购入库'),  # CGRK=采购入库;
        ('DBRK', '调拨入库'),  # DBRK= 调拨入库;
        ('QTRK', '其他入库'),  # QTRK= 其他入库;
        ('XTRK', '销退入库'),  # XTRK= 销退入库;
        ('HHRK', '换货入库'),  # HHRK= 换货入库;
        ('CNJG', '仓内加工单'),  # CNJG= 仓内加工单
    )
    id = models.AutoField(primary_key=True)

    # ownerCode String 必须 H1234货主编码
    owner_code = models.CharField(max_length=20, verbose_name='货主编码')
    # warehouseCode String 必须 CH1234仓库编码
    warehouse_code = models.CharField(max_length=20, verbose_name='仓库编码')
    warehouse_id = models.CharField(
        max_length=20,
        null=True,
        verbose_name='仓库id')
    warehouse_name = models.CharField(
        max_length=32,
        null=True,
        verbose_name='仓库名称')

    inventory_type = models.CharField(
        max_length=10,
        choices=INVENTORY_TYPE,
        verbose_name='库存类型')

    order_code = models.CharField(max_length=30, verbose_name='引起异动的单据编码')
    order_type = models.CharField(
        max_length=20,
        verbose_name='单据类型',
        choices=ORDER_TYPE)

    out_biz_code = models.CharField(max_length=30, verbose_name='外部业务编码')
    item_code = models.CharField(max_length=30, verbose_name='商家编码')
    item_id = models.CharField(max_length=30, verbose_name='仓储系统商品ID')

    quantity = models.IntegerField(verbose_name='商品变化量(可为正为负)')
    batch_code = models.CharField(max_length=30, null=True, verbose_name='批次编码')
    product_date = models.DateTimeField(null=True, verbose_name='商品生产日期(YYYY-MM-DD)')
    expire_date = models.DateTimeField(null=True, verbose_name='商品过期日期(YYYY-MM-DD)')
    produce_code = models.CharField(null=True, max_length=30, verbose_name='生产批号')
    change_tiem = models.\
        DateTimeField(null=True, verbose_name='异动时间(YYYY-MM-DD HH:MM:SS)')

    class Meta:
        db_table = 'stockchange_report'
