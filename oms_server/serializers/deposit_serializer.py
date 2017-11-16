from rest_framework.serializers import ModelSerializer, SerializerMethodField
from oms.models.deposit_detail import DepositDetail
from oms_server.serializers.extension import TimestampField


STATEMENT_TYPE = {
    1: '充值',
    2: '提现'
}


class DepositDetailSerializer(ModelSerializer):

    created_at = TimestampField()

    statement_type_value = SerializerMethodField()

    def get_statement_type_value(self, obj):
        return STATEMENT_TYPE.get(obj.statement_type)

    class Meta:
        model = DepositDetail
        fields = ('id', 'created_at', 'amount', 'is_receipt',
                  'statement_type', 'statement_type_value')
