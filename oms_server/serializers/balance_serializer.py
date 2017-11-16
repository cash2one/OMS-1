from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import SerializerMethodField
from oms.models.receipt_disbursement_statement import\
    ReceiptDisbursementStatement
from oms_server.serializers.extension import TimestampField

STATEMENT_TYPE = {
    1: '充值',
    2: '预充值',
    3: '保证金',
    4: '订单收入',
    5: '账单收入',
    6: '仓储收入',
    11: '账单支出',
    12: '面单费用支出',
    13: '提现'
}


class ReceiptDisbursenmentSerializer(ModelSerializer):

    created_at = TimestampField()

    statement_type_value = SerializerMethodField()

    def get_statement_type_value(self, obj):
        return STATEMENT_TYPE.get(obj.statement_type)

    class Meta:

        model = ReceiptDisbursementStatement
        fields = ('id', 'created_at', 'is_receipt',
                  'amount', 'statement_type', 'statement_type_value')
