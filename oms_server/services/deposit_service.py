import time
import json
import logging
from django.db import transaction
from django.conf import settings
from oms.models.deposit import Deposit
from oms.models.withdraw import Withdraw
from oms.models.deposit_detail import DepositDetail
from oms.extension.exception import CustomException
from oms_server.services.charge_service import ChargeService
"""
保证金相关逻辑
"""
logger = logging.getLogger('custom.deposit')


class DepositService:

    def show_deposit(self, user_id):
        ''' 显示保证金 '''
        deposit, _ = Deposit.objects.\
            only('amount').\
            get_or_create(user_id=user_id)
        return deposit.amount

    def details(self, user_id):
        ''' 保证金明细 '''
        deposti_details = DepositDetail.objects.\
            filter(user_id=user_id)
        return deposti_details

    def add_deposit(self, user_id, amount):
        ''' 增加保证金 '''
        deposit, _ = Deposit.objects.get_or_create(user_id=user_id)
        deposit.amount += amount
        deposit.save()
        return deposit.amount

    def deduct_deposit(self, user_id, amount):
        ''' 扣减保证金 '''
        deposit, _ = Deposit.objects.get_or_create(user_id=user_id)
        deposit.amount -= amount
        deposit.save()
        return deposit.amount

    def receipt_deposit(self, user_id, amount):
        ''' 保证金充值记录 '''
        deposit_detail = DepositDetail(
            user_id=user_id,
            is_receipt=True,
            amount=amount,
            statement_type=1
        )
        deposit_detail.save()
        return deposit_detail

    def disbursement_deposit(self, user_id, amount):
        ''' 保证金提现记录 '''
        deposit_detail = DepositDetail(
            user_id=user_id,
            is_receipt=False,
            amount=amount,
            statement_type=2
        )
        deposit_detail.save()
        return deposit_detail

    @transaction.atomic
    def charge(self, user_id, amount, channel, client_ip, extra={}):
        ''' 保证金充值 '''
        deposit = self.show_deposit(user_id)
        charge_ser = ChargeService()
        ch = charge_ser.\
            pay(user_id=user_id, amount=amount, channel=channel,
                pay_type=3, client_ip=client_ip, extra=extra)
        charge_ser.create_charge(ch=ch, pay_type=3, user_id=user_id)
        logger.info('用户{0}：保证金充值:{1},当前余额:{2}'.
                    format(user_id, amount, deposit))
        return ch

    @transaction.atomic
    def withdraw(self, user_id, amount, channel,
                 recipient, recipient_name):
        ''' 保证金提现 '''
        deposit = self.show_deposit(user_id)
        if deposit < amount:
            raise CustomException(40008, '提现金额大于保证金余额！')
        description = '仓妈咪账户保证金提现'
        self.deduct_deposit(user_id, amount)
        withdraw = Withdraw(
            withdraw_type=2,
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
        logger.info('用户{0},{1}：提现保证金:{2}'.
                    format(user_id, recipient_name, amount))
        return withdraw

