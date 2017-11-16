# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


class Sku(BaseModel):

    UNIT_CHOICES = (
        ('kg.', '千克'),
    )

    id = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name='sku编码',
        editable=False)

    item_code = models.CharField(null=True, max_length=20, verbose_name='奇门编码')

    outer_item_code = models.\
        CharField(max_length=64, null=True, verbose_name='第三方编码')

    sku_name = models.CharField(max_length=128, verbose_name='商品名称')

    specification = models.CharField(null=True, max_length=128, verbose_name='商品规格')

    bar_code = models.CharField(null=True, max_length=64, verbose_name='商品条码')

    # user_code = models.CharField(max_length=64, verbose_name='商家编码')

    price = models.FloatField(default=0.0, verbose_name='商家价格')

    unit = models.\
        CharField(default='kg', max_length=10, choices=UNIT_CHOICES, verbose_name='商品单位')

    goods_no = models.CharField(null=True, max_length=64, verbose_name='货号')
    sku_version = models.IntegerField(default=0, null=True)
    item_type = models.CharField(null=True, max_length=20, verbose_name='产品类型')

    brand = models.CharField(null=True, max_length=20, verbose_name='产品品牌编码')
    brand_name = models.CharField(null=True, max_length=20, verbose_name='产品品牌名称')
    color = models.CharField(null=True, max_length=10)
    size = models.CharField(null=True, max_length=10)
    gross_weight = models.IntegerField(default=0, verbose_name='毛重，单位克')
    net_weight = models.IntegerField(default=0, verbose_name='净重，单位克')
    length = models.IntegerField(default=0, verbose_name='单位毫米')
    width = models.IntegerField(default=0, verbose_name='单位毫米')
    height = models.IntegerField(default=0, verbose_name='单位毫米')
    volume = models.IntegerField(default=0, verbose_name='单位立方厘米')
    pcs = models.IntegerField(default=0, verbose_name='箱规')

    quantity = models.IntegerField(default=0, verbose_name='Sku数量')

    available_quantity = models.IntegerField(default=0, verbose_name='可用Sku数量')
    is_shelflife = models.BooleanField(default=False, verbose_name='是否启用保质期管理')
    lifecycle = models.IntegerField(default=0, verbose_name='保质期天数')
    reject_lifecycle = models.IntegerField(default=0, verbose_name='保质期禁收天数')
    lockup_lifecycle = models.IntegerField(default=0, verbose_name='保质期禁售天数')
    advent_lifecycle = models.IntegerField(default=0, verbose_name='保质期临期天数')
    is_sn_mgt = models.BooleanField(default=False)
    is_hygroscopic = models.BooleanField(default=False)
    is_danger = models.BooleanField(default=False)

    # 是否存在? 订单中出现了不存在的sku
    is_exist = models.BooleanField(default=True)

    # 关联字段
    category = models.ForeignKey('oms.SkuCategory', null=True, verbose_name='产品类别')
    category_name = models.CharField(max_length=20, verbose_name='产品类别名称')
    user_id = models.IntegerField(null=False, verbose_name='用户id')
    # owner = models.ForeignKey('oms.User', null=True, verbose_name='所属商户')

    # 覆盖内建的删除方法
    # 检查库存是否为空
    # 在批量删除时，不会调用
    # 需要实现pre_delelte方法
    # def delete(self, *args, **kwargs):
    #     pass

    def __str__(self):
        return self.sku_name

    class Meta:
        ordering = ['-created_at']
        app_label = 'oms'
        db_table = 'sku'
        unique_together = (('user_id', 'item_code'),)
