# -*- coding: UTF-8 -*-
from django.db import models
from .base import BaseModel


# 最小活动单元
class ActivityRule(BaseModel):

    RULE_TYPES = (
        (1, '满元赠'),
        (2, '满件赠')
    )
    id = models.AutoField(primary_key=True)

    is_expired = models.NullBooleanField(default=False, verbose_name='是否过期')

    is_enabled = models.NullBooleanField(default=False, verbose_name='是否开启')

    title = models.CharField(max_length=32, null=False, verbose_name='活动标题')

    begin_date = models.DateTimeField(
        null=False,
        verbose_name='开始时间')

    end_date = models.DateTimeField(
        null=False,
        verbose_name='结束时间')

    rule_type = models.\
        IntegerField(default=1, choices=RULE_TYPES, verbose_name='活动规则类型')

    # 满元赠活动
    accord_cost = models.FloatField(default=0, null=True, verbose_name='满足价格')

    is_times = models.NullBooleanField(
        default=False,
        verbose_name='是否开启倍增，只适用满元赠')

    # 满件赠活动
    accord_amount = models.\
        IntegerField(default=0, null=True, verbose_name='满足数量')

    user_id = models.IntegerField(null=False, verbose_name='用户id')

    store = models.ForeignKey('oms.Store', null=False, verbose_name='所属店铺')

    # 活动商品　和　赠品,通过ActivitySku多对多关联
    activity_skues = models.ManyToManyField(
        'oms.Sku',
        through='oms.ActivitySku',
        verbose_name='活动商品/赠品')

    # gifts = models.ManyToManyField(
    #     'oms.Sku',
    #     through='oms.ActivitySku',
    #     verbose_name='活动商品/赠品')

    class Meta:
        ordering = ['-created_at']
        db_table = 'activity_rule'
