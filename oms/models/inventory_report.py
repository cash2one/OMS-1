from django.db import models
from .base import BaseModel


class InventoryReport(BaseModel):

    id = models.AutoField(primary_key=True)
    # totalPage Number 总页数
    total_page = models.IntegerField(null=True, verbose_name='总页数')
    # currentPage Number  当前页(从1开始)
    receive_pages = models.\
        CharField(null=True, max_length=50, verbose_name='已经收到的页面用分号区分')
    # pageSize Number 每页记录的条数
    page_size = models.IntegerField(null=True, verbose_name='每页记录的条数')
    warehouse_code = models.CharField(max_length=20, verbose_name='仓库编码')
    warehouse_id = models.CharField(
        max_length=20,
        null=True,
        verbose_name='仓库id')
    warehouse_name = models.CharField(
        max_length=32,
        null=True,
        verbose_name='仓库名称')
    check_order_code = models.CharField(max_length=30, verbose_name='盘点单编码')
    check_order_id = models.\
        CharField(max_length=20, verbose_name='仓储系统的盘点单编码')
    owner_code = models.CharField(max_length=20, verbose_name='货主编码')
    # user_id = models.IntegerField(null=False, verbose_name='用户id')
    check_time = models.DateTimeField(null=True, verbose_name='盘点时间')
    out_biz_code = models.CharField(max_length=30, verbose_name='外部业务编码')
    remark = models.CharField(max_length=100, verbose_name='备注')

    class Meta:
        ordering = ['-created_at']
        db_table = 'inventory_report'
