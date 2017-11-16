# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer
from oms.models.sku import Sku
from oms.models.sku_warehouse import SkuWarehouse
from rest_framework.serializers import StringRelatedField, IntegerField, Field
from oms_server.serializers.extension import TimestampField


class InvetorySerializer(ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    sku_name = StringRelatedField(source='sku.sku_name', required=False)
    item_code = StringRelatedField(source='sku.item_code', required=False)
    bar_code = StringRelatedField(source='sku.bar_code', required=False)
    specification = StringRelatedField(source='sku.specification', required=False)

    class Meta:
        model = SkuWarehouse
        fields = ('id', 'created_at', 'updated_at', 'quantity',
                  'available_quantity', 'warehouse_name', 'user_id',
                  'sku_name', 'item_code', 'bar_code', 'specification')


class NoneField(Field):

    def to_internal_value(self, data):
        return int(data)

    def to_representation(self, value):
        if value is None:
            return ''
        return value


class SkuSerializer(ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    category_name = NoneField(required=False)
    category_id = NoneField(required=True, allow_null=False)
    inventories = InvetorySerializer(many=True, required=False)

    class Meta:
        model = Sku
        fields = ('id', 'created_at', 'updated_at', 'sku_name', 'quantity',
                  'specification', 'bar_code', 'item_code', 'available_quantity',
                  'price', 'unit', 'category_id', 'is_deleted', 'category_name',
                  'inventories')
