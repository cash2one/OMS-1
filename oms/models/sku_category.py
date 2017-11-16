# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


# 商品目录表
class SkuCategory(BaseModel):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=20, verbose_name='目录名称')
    # category_desc = models.CharField(max_length=20, verbose_name='目录描述')

    user_id = models.IntegerField(null=False, verbose_name='用户id')

    super_category = models.\
        ForeignKey('self', null=True, related_name='sub_category')

    def __str__(self):
        return self.category_name

    class Meta:
        ordering = ['-created_at']
        app_label = 'oms'
        db_table = 'oms_sku_category'
