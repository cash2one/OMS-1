# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


class Store(BaseModel):

    DEVELOPMENT_TYPE = (
        ('isv', 'isv'),
        ('personal', '自建')
        )
    id = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name='店铺id',
        editable=False)
    auto_check = models.BooleanField(default=True, verbose_name='是否自动审核')
    auto_merge = models.BooleanField(default=True, verbose_name='是否自动合并订单')
    is_enabled = models.BooleanField(default=True, verbose_name='是否启用')
    fetch_order_latest = models.\
        DateTimeField(auto_now=False, null=True, verbose_name='最近抓取订单时间')

    store_key = models.\
        CharField(
            max_length=20,
            null=True, verbose_name='店铺平台id'
        )
    store_development_type = models.\
        CharField(max_length=20,
                  default='isv',
                  choices=DEVELOPMENT_TYPE,
                  verbose_name='商家用户类型')

    # 店铺属性
    store_name = models.CharField(max_length=40, blank=False, verbose_name='店铺名称')

    username = models.CharField(max_length=40, blank=False, verbose_name='商家名称')

    address = models.CharField(null=True, max_length=100, verbose_name='具体地址')

    contact_number = models.CharField(null=True, max_length=20, verbose_name='联系电话')

    abbreviation = models.CharField(null=True, max_length=100, verbose_name='店铺简称')

    # 店铺配置
    app_key = models.CharField(max_length=80, verbose_name='app_key')

    app_secret = models.CharField(max_length=512, verbose_name='app_secret')

    access_token = models.CharField(null=True, max_length=512, verbose_name='访问令牌')

    refresh_token = models.CharField(null=True, max_length=512, verbose_name='刷新令牌')

    expire_in = models.IntegerField(default=0, null=True)

    access_token_expire_time = models.\
        DateTimeField(null=True, verbose_name='访问令牌过期时间')

    refresh_token_expire_time = models.\
        DateTimeField(null=True, verbose_name='刷新令牌过期时间')

    # 关联关系
    platform = models.ForeignKey('oms.Plat', null=False, verbose_name='电商平台')
    platform_name = models.CharField(max_length=32, null=False, verbose_name='电商平台名称')
    user_id = models.IntegerField(null=False, verbose_name='用户id')
    # owner = models.ForeignKey('oms.User', null=True, verbose_name='所属用户')

    class Meta:
        ordering = ['-created_at']
        app_label = 'oms'
        db_table = 'store'

    def __str__(self):
        return self.store_name
