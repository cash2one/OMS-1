from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from oms.models.order_bill import OrderBill
from oms.models.storge_bill import StorgeBill
from oms_server.serializers.extension import TimestampField


class OrderBillSerializer(ModelSerializer):

    created_at = TimestampField()
    bill_type = SerializerMethodField()
    bill_type_value = SerializerMethodField()

    def get_bill_type(self, obj):
        return 1

    def get_bill_type_value(self, obj):
        return '发货账单'

    class Meta:
        model = OrderBill
        fields = ('id', 'created_at', 'amount', 'paid',
                  'warehouse_name', 'warehouse_id',
                  'bill_type', 'bill_type_value',
                  'express_amount', 'express_sheet_amount',
                  'order_process_amount', 'unsettle_amount',
                  'order_id', 'order_code', 'order_process_fee_id')


class StorgeBillSerializer(ModelSerializer):

    created_at = TimestampField()
    bill_type = SerializerMethodField()
    bill_type_value = SerializerMethodField()

    def get_bill_type(self, obj):
        return 2

    def get_bill_type_value(self, obj):
        return '仓储账单'

    class Meta:
        model = StorgeBill
        fields = ('id', 'created_at', 'amount', 'warehouse_id',
                  'bill_type', 'bill_type_value',
                  'warehouse_name', 'paid', 'storge_fee_id')