# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.serializers import CharField, DateTimeField
from oms.models import Store
from oms_server.serializers.extension import TimestampField
from oms_server.serializers.extension import UUIDField


PLATFORM = {
    'jingdong': '京东',
    'taobao': '淘宝',
    'tianmao': '天猫',
    'youzan': '有赞',
    'youdan': '优蛋',
    'weidian': '微店',
    'yidianbao': 'E店宝',
    'yidinghuo': '易订货',
    'juanpi': '卷皮',
    'pinduoduo': '拼多多'
}


class StoreSerializer(ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    store_key = CharField(required=False)
    refresh_token_expire_time =\
        TimestampField(required=False)
    access_token_expire_time =\
        TimestampField(required=False)
    platform_id = UUIDField()
    platform_name = SerializerMethodField()

    def get_platform_name(self, obj):
        if not obj.platform_name:
            return ''
        else:
            return PLATFORM.get(obj.platform_name)

    def get(self, store_id):
        return Store.objects.get(pk=store_id)

    class Meta:
        model = Store
        fields = ('id', 'created_at', 'updated_at', 'auto_check',
                  'auto_merge', 'is_enabled', 'fetch_order_latest',
                  'is_deleted',
                  'store_key', 'store_development_type', 'store_name',
                  'username', 'address', 'contact_number', 'abbreviation',
                  'app_key', 'app_secret', 'access_token', 'refresh_token',
                  'expire_in', 'access_token_expire_time',
                  'refresh_token_expire_time', 'platform_name', 'platform_id')
