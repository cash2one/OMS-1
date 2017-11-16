# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer
from oms.models.stock_in import StockIn
from oms.models.stock_in_detail import StockInDetail
from oms_server.serializers.extension import TimestampField
from oms_server.serializers.extension import UUIDField


class StockInDetailSerializer(ModelSerializer):
    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)

    class Meta:
        model = StockInDetail
        fields = ('id', 'created_at', 'updated_at', 'quantity',
                  'sku_name', 'sku_spec', 'item_code', 'bar_code',
                  'sku_id')


class StockInSerializer(ModelSerializer):

    created_at = TimestampField(required=False)
    updated_at = TimestampField(required=False)
    estimated_to_arrival = TimestampField(required=False)
    stock_in_details = StockInDetailSerializer(many=True, required=False)
    warehouse_id = UUIDField()

    class Meta:
        model = StockIn
        fields = ('id', 'created_at', 'updated_at', 'stock_in_type',
                  'stock_in_status', 'entry_order_id', 'order_code',
                  'user_note', 'express', 'express_number',
                  'estimated_to_arrival', 'warehouse_name', 'warehouse_id',
                  'stock_in_details', 'user_mobile',
                  'user_id', 'user_name'
                  )
