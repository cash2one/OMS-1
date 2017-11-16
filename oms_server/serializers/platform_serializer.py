# -*- coding: UTF-8 -*-
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from oms_server.serializers.extension import TimestampField
from oms.models.plat import Plat
from oms_server.serializers.extension import UUIDField


PLATFORM = {
    'jingdong': '京东',
    'taobao': '淘宝',
    'tmall': '天猫',
    'youzan': '有赞',
    'youdan': '优蛋',
    'weidian': '微店',
    'yidianbao': 'E店宝',
    'yidinghuo': '易订货',
    'juanpi': '卷皮',
    'pinduoduo': '拼多多',
    'yihaodian': '一号店',
    'vip': '唯品会',
    'suning': '苏宁',
    'yemaijiu': '也买酒',
    'jiuxianwang': '酒仙网',
    'jumeiyoupin': '聚美优品',
    'amazon': '亚马逊',
    'dangdang': '当当',
    'nuomiwang': '糯米网',
    'zhongliang': '中粮我买网'
}


class PlatformSerializer(ModelSerializer):

    # id = UUIDField(required=False)

    name = SerializerMethodField()

    def get_name(self, obj):
        if not obj.name:
            return ''
        else:
            return PLATFORM.get(obj.name)

    class Meta:
        model = Plat
        fields = [
            'id', 'name', 'need_store_key', 'need_app_key', 'need_app_secret'
        ]
