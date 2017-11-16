import time
import logging
import datetime
import requests
from django.db import transaction
from oms.models.charge import Charge
from oms.models.order_bill import OrderBill
from oms.models.storge_bill import StorgeBill
from oms.models.overdue_bill import OverdueBill
from oms.models.withdraw import Withdraw
from oms_server.services.balance_service import BalanceService
from oms_server.services.deposit_service import DepositService
from oms_server.services.receipt_disbursement_service import\
    ReceiptDisbursementService
from oms.extension.exception import PingppException

logger = logging.getLogger('custom.pingpp')


''' Ping++回调 '''


class PingppCallbackService:

    @transaction.atomic
    def paid(self, ch):
        ''' 支付完成回调，支持失败重试机制 '''
        charge = None
        try:
            charge = Charge.objects.\
                get(charge_id=ch['data']['object']['id'])
        except Charge.DoesNotExist as e:
            logger.warn('支付凭证不存在:%s' % ch['data']['object']['id'])
            raise PingppException('支付凭证不存在')
        # 修改支付凭证状态
        try:
            charge.paid = True
            charge.time_paid = int(time.time())
            charge.save()
            if charge.pay_type == 3:  # 保证金充值
                # 保证金增加
                deposit_ser = DepositService()
                deposit_ser.\
                    add_deposit(user_id=charge.user_id,
                                amount=charge.amount)
                # 记录流水
                deposit_ser.\
                    receipt_deposit(user_id=charge.user_id,
                                    amount=charge.amount)
            elif charge.pay_type == 1:  # 余额充值
                BalanceService().\
                    add_balance(user_id=charge.user_id,
                                amount=charge.amount)
                ReceiptDisbursementService().\
                    receipt(user_id=charge.user_id,
                            statement_type=1,
                            amount=charge.amount)
            elif charge.pay_type == 2:  # 账单支付
                # 找到支付凭证关联的账单
                order_bills = OrderBill.objects.\
                    filter(user_id=charge.user_id,
                           charge_id=charge.id)
                storge_bills = StorgeBill.objects.\
                    filter(user_id=charge.user_id,
                           charge_id=charge.id)
                overdue_bill = OverdueBill.objects.\
                    filter(user_id=charge.user_id,
                           charge_id=charge.id)
                # 修改账单状态
                now = datetime.datetime.now()
                for ob in order_bills:
                    ob.paid = True
                    ob.paid_time = now
                    ob.save()
                for sb in storge_bills:
                    sb.paid = True
                    sb.paid_time = now
                    sb.save()
                if overdue_bill:
                    overdue_bill.paid = True
                    overdue_bill.paid_time = now
                    overdue_bill.save()
            elif charge.pay_type == 4:  # 开发者认证支付
                # 发起掉用仓妈咪相关接口
                result = requests.\
                    get(url='http://47.95.235.167:8002/api/developers/paid?user_id=' + str(charge.user_id)).\
                    json()
                print(result)
                print("ooooooooooooooooooooooo")
        except Exception as e:
            raise PingppException(str(e))
        return True

    def withdrawed(self, w):
        ''' 提现成功 '''
        try:
            obj = w['data']['object']
            if obj['type'] == 'transfer.succeeded':
                withdraw = Withdraw.objects.get(transfer_id=obj['id'])
                withdraw.status = obj['status']
                withdraw.save()
        except Exception as e:
            raise PingppException(str(e))
        return {'success': 'success'}
