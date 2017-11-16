# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.serializers import StringRelatedField, CharField
from oms.models.order import Order
from oms.models.order_detail import OrderDetail
from oms_server.serializers.extension import\
    TimestampField, UUIDField, StatusField


class OrderDetailSerializer(ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    sku_name = StringRelatedField(source='sku.sku_name')
    specification = StringRelatedField(source='sku.specification')
    bar_code = StringRelatedField(source='sku.bar_code')
    item_code = StringRelatedField(source='sku.item_code', default='')
    price = StringRelatedField(source='sku.price')
    sku_id = CharField(source='sku.id')
    available_quantity = StringRelatedField(source='sku.available_quantity')

    class Meta:

        model = OrderDetail
        fields = [
            'id', 'created_at', 'updated_at', 'is_gift', 'price',
            'quantity', 'sku_name', 'bar_code', 'item_code',
            'available_quantity', 'specification', 'sku_id'
        ]


class OrderSerializer(ModelSerializer):

    # id = UUIDField(required=False)
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    store_name = StringRelatedField(source='store.store_name')
    order_code = CharField(read_only=True)
    store_name = StringRelatedField(source='store.store_name')
    buyer_nickname = CharField(read_only=True)
    order_details = OrderDetailSerializer(many=True, required=False)
    express = CharField(source='logistics_name')
    wms_status = StatusField()
    order_status = StatusField()
    order_mark = StatusField()
    # express_number = SerializerMethodField()

    # def get_express_number(self, obj):
    #     if hasattr(obj, 'order_express'):
    #         express_number = ','.\
    #             join([e.express_code for e in obj.order_express])
    #         return express_number
    #     else:
    #         return ''

    class Meta:

        model = Order
        fields = ['id', 'created_at', 'updated_at', 'is_locked', 'is_splited',
                  'order_mark', 'order_status', 'wms_status', 'total_price',
                  'express', 'zip_code', 'warehouse_name', 'express_number',
                  'order_code', 'store_name', 'buyer_nickname',
                  'consignee_name', 'consignee_phone', 'consignee_province',
                  'consignee_city', 'consignee_area', 'consignee_detail',
                  'buyer_note', 'user_note', 'order_details',
                  'user_id', 'user_name'
                  ]
