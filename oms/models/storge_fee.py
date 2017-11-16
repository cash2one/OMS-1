from django.db import models
from .base import BaseModel

"""
仓库存储费用
"""


class StorgeFee(BaseModel):

    id = models.AutoField(primary_key=True)

    volume = models.FloatField(default=0.0, verbose_name='商品体积')

    amount = models.IntegerField(verbose_name='总金额(单位分)')

    warehouse_id = models.CharField(max_length=20, verbose_name='仓库id')

    warehouse_name = models.CharField(max_length=50, verbose_name='仓库名称')

    class Meta:
        ordering = ['-created_at']
        db_table = 'storge_fee'
