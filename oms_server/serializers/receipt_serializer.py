from rest_framework.serializers import ModelSerializer
from oms.models.order_receipt import OrderReceipt
from oms.models.storge_receipt import StorgeReceipt
from oms_server.serializers.extension import TimestampField


class OrderReceiptSerializer(ModelSerializer):

    created_at = TimestampField()

    class Meta:
        model = OrderReceipt
        fields = ('id', 'created_at', 'amount',
                  'warehouse_name', 'warehouse_id',
                  'express_amount',
                  'order_process_amount',
                  'order_id', 'order_code', 'order_process_fee_id')


class StorgeReceiptSerializer(ModelSerializer):

    created_at = TimestampField()

    class Meta:
        model = StorgeReceipt
        fields = ('id', 'created_at', 'amount', 'warehouse_id',
                  'warehouse_name', 'storge_fee_id')