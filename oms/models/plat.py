# -*- coding: utf-8 -*-
from django.db import models
from .base import BaseModel


class Plat(BaseModel):
    STORE_PLAT_IN_CHOICE = (
        ('jingdong', '京东'),
        ('taobao', '淘宝'),
        ('tmall', '天猫'),
        ('youzan', '有赞'),
        ('youdan', '优蛋'),
        ('weidian', '微店'),
        ('yidianbao', 'E店宝'),
        ('yidinghuo', '易订货'),
        ('juanpi', '卷皮'),
        ('pinduoduo', '拼多多'),
        ('yihaodian', '一号店'),
        ('vip', '唯品会'),
        ('suning', '苏宁'),
        ('yemaijiu', '也买酒'),
        ('jiuxianwang', '酒仙网'),
        ('jumeiyoupin', '聚美优品'),
        ('amazon', '亚马逊'),
        ('dangdang', '当当'),
        ('nuomiwang', '糯米网'),
        ('zhongliang', '中粮我买网')
    )

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=20,
        choices=STORE_PLAT_IN_CHOICE)
    interface = models.CharField(max_length=20, null=True)
    callback = models.URLField(null=True)
    is_jointed = models.BooleanField(default=False)
    need_store_key = models.BooleanField(default=True,
                                         verbose_name='是否需要store_key')
    need_app_key = models.BooleanField(default=True,
                                       verbose_name='是否需要app_key')
    need_app_secret = models.BooleanField(default=True,
                                          verbose_name='是否需要app_secret')

    class Meta:
        ordering = ['-created_at']
        app_label = 'oms'
        db_table = 'platform'

    def __str__(self):
        return self.name
