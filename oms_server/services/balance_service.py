import time
import json
import logging
from django.conf import settings
from django.db import transaction
from django.core.paginator import Paginator
from oms.models.balance import Balance
from oms.models.withdraw import Withdraw
from oms.models.receipt_disbursement_statement import\
    ReceiptDisbursementStatement
from oms.extension.exception import CustomException
from oms_server.services.charge_service import ChargeService


"""
用户余额相关逻辑
"""

logger = logging.getLogger('custom.balance')


class BalanceService:

    def show_balance(self, user_id):
        ''' 显示余额 '''
        balance, _ = Balance.objects.\
            only('amount').\
            get_or_create(user_id=user_id)
        return balance.amount

    def recent(self, user_id):
        ''' 最近余额明细 '''
        rds = ReceiptDisbursementStatement.objects.\
            filter(user_id=user_id).\
            order_by('-created_at')[:8]
        return rds

    def hava_balance(self, user_id):
        ''' 是否有余额 '''
        balance, _ = Balance.objects.\
            only('amount').\
            get_or_create(user_id=user_id)
        return balance.amount > 0

    def statistics_ios(self, user_id, statement_type, page_size,
                       is_receipt=None):
        ''' ios专用余额明细 '''
        paginator = None
        if is_receipt is None:
            if not statement_type or int(statement_type) <= 0:
                query_set = ReceiptDisbursementStatement.objects.\
                    filter(user_id=user_id)
            else:
                query_set = ReceiptDisbursementStatement.objects.\
                    filter(user_id=user_id,
                           statement_type=int(statement_type))
        elif is_receipt is True:
            query_set = ReceiptDisbursementStatement.objects.\
                filter(user_id=user_id,
                       statement_type__lt=10)
        else:
            query_set = ReceiptDisbursementStatement.objects.\
                filter(user_id=user_id,
                       statement_type__gt=10)
        paginator = Paginator(query_set, per_page=page_size)
        return paginator

    def statistics(self, user_id, statement_type, page_size,
                   start_time, end_time, is_receipt=None):
        ''' 余额明细 '''
        paginator = None
        if is_receipt is None:
            if not statement_type or int(statement_type) <= 0:
                query_set = ReceiptDisbursementStatement.objects.\
                    filter(user_id=user_id,
                           created_at__range=(start_time, end_time))
            else:
                query_set = ReceiptDisbursementStatement.objects.\
                    filter(user_id=user_id,
                           created_at__range=(start_time, end_time),
                           statement_type=int(statement_type))
        elif is_receipt is True:
            query_set = ReceiptDisbursementStatement.objects.\
                filter(user_id=user_id,
                       created_at__range=(start_time, end_time),
                       statement_type__lt=10)
        else:
            query_set = ReceiptDisbursementStatement.objects.\
                filter(user_id=user_id,
                       created_at__range=(start_time, end_time),
                       statement_type__gt=10)
        paginator = Paginator(query_set, per_page=page_size)
        return paginator

    def add_balance(self, user_id, amount):
        ''' 增加余额 '''
        balance, _ = Balance.objects.get_or_create(user_id=user_id)
        balance.amount += amount
        balance.save()
        logger.info('用户{0}：增加余额:{1},剩余余额:{2}'.
                    format(user_id, amount, balance.amount))
        return balance.amount

    def deduct_balance(self, user_id, amount):
        ''' 扣减余额 '''
        balance, _ = Balance.objects.get_or_create(user_id=user_id)
        balance.amount -= amount
        balance.save()
        logger.info('用户{0}：扣减余额:{1},剩余余额:{2}'.
                    format(user_id, amount, balance.amount))
        return balance.amount

    @transaction.atomic
    def charge_balance(self, user_id, amount, channel, client_ip, extra={}):
        ''' 余额充值 '''
        balance = self.show_balance(user_id)
        charge_ser = ChargeService()
        ch = charge_ser.\
            pay(user_id=user_id, amount=amount, channel=channel,
                pay_type=2, client_ip=client_ip, extra=extra)
        charge_ser.create_charge(ch=ch, pay_type=1, user_id=user_id)
        logger.info('用户{0}：充值:{1},当前余额:{2}'.
                    format(user_id, amount, balance))
        return ch

    @transaction.atomic
    def withdraw_balance(self, user_id, amount, channel,
                         recipient, recipient_name):
        ''' 余额提现 '''
        balance = self.show_balance(user_id)
        if amount > balance:
            raise CustomException(40003, '提现金额大于账户余额')
        description = '仓妈咪账户余额提现'
        withdraw = Withdraw(
            withdraw_type=1,
            user_id=user_id,
            amount=amount,
            order_no=str(int(time.time())),
            channel=channel,
            currency='cny',
            app=settings.PINGXX_APPID,
            recipient=recipient,
            extra=json.dumps(dict(recipient_name=recipient_name)),
            description=description
        )
        withdraw.save()
        logger.info('用户{0},{1}：申请提现:{2}'.
                    format(user_id, recipient_name, amount))
        return withdraw
        

