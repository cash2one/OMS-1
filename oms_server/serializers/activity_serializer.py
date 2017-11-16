# -*- coding: UTF-8 -*-
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import StringRelatedField
from oms.models.activity_rule import ActivityRule
from oms_server.serializers.extension import TimestampField
from oms_server.serializers.extension import UUIDField


class SkuField(serializers.RelatedField):

    def to_representation(self, value):
        if value.is_gift is False:
            result = {
                'item_id': str(value.id).replace('-', ''),
                'sku_id': str(value.sku.id).replace('-', ''),
                'sku_name': value.sku.sku_name,
                'count': value.count,
                'sku_specification': value.sku.specification,
                'sku_bar_code': value.sku.bar_code,
                'sku_seller_code': value.sku.item_code
            }
            return result


class GiftField(serializers.RelatedField):

    def to_representation(self, value):
        if value.is_gift:
            result = {
                'sku_id': str(value.sku.id).replace('-', ''),
                'item_id': str(value.id).replace('-', ''),
                'sku_name': value.sku.sku_name,
                'count': value.count,
                'sku_specification': value.sku.specification,
                'sku_bar_code': value.sku.bar_code,
                'sku_seller_code': value.sku.item_code
            }
            return result


class ActivityListSerializer(ModelSerializer):

    # id = UUIDField(required=False)
    # store_id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    begin_date = TimestampField(required=False)
    end_date = TimestampField(required=False)
    store_name = StringRelatedField(source='store.store_name')

    class Meta:
        model = ActivityRule
        fields = [
            'id', 'store_id', 'created_at', 'updated_at', 'begin_date',
            'is_enabled',
            'end_date', 'is_expired', 'title', 'rule_type', 'accord_cost',
            'is_times', 'accord_amount', 'store_name', 'is_deleted'
        ]


class ActivitySerializer(ModelSerializer):

    # id = UUIDField(required=False)
    # store_id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    begin_date = TimestampField(required=False)
    end_date = TimestampField(required=False)
    skues = SkuField(many=True, read_only=True, required=False)
    gifts = GiftField(many=True, read_only=True, required=False)
    store_name = StringRelatedField(source='store.store_name')

    class Meta:
        model = ActivityRule
        fields = [
            'id', 'store_id', 'created_at', 'updated_at', 'begin_date',
            'is_enabled',
            'end_date', 'is_expired', 'title', 'rule_type', 'accord_cost',
            'is_times', 'accord_amount', 'store_name', 'skues', 'gifts'
        ]
