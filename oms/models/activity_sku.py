# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


# 活动商品或者是赠品
class ActivitySku(BaseModel):

    id = models.AutoField(primary_key=True)

    is_gift = models.NullBooleanField(default=False, verbose_name='是否是赠品')

    count = models.IntegerField(default=1, verbose_name='赠品数量')

    # 增加冗余
    # sku_name = models.CharField(max_length=128, verbose_name='商品名称')
    #
    # specification = models.CharField(max_length=20, verbose_name='商品规格')
    #
    # bar_code = models.CharField(max_length=64, verbose_name='商品条码')
    #
    # seller_code = models.CharField(max_length=64, verbose_name='商家编码')

    activity_rule = models.\
        ForeignKey('oms.ActivityRule', null=False, verbose_name='活动规则')

    sku = models.\
        ForeignKey('oms.Sku', null=False, verbose_name='赠品或者是商品')

    def __str__(self):
        return 'Activity sku : ' + self.sku.name

    class Meta:
        ordering = ['-created_at']
        app_label = 'oms'
        db_table = 'activity_sku'
