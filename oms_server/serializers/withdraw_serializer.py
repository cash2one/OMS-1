from rest_framework.serializers import ModelSerializer
from oms.models.withdraw import Withdraw
from oms_server.serializers.extension import TimestampField


class WithdrawSerializer(ModelSerializer):

    created_at = TimestampField()

    class Meta:
        model = Withdraw
        fields = ('id', 'created_at', 'amount', 'status',
                  'status_info', 'recipient',
                  'channel')

