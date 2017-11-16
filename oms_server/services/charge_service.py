import os
import time
import logging
import pingpp
from django.conf import settings
from oms.models.charge import Charge
from oms.models.withdraw import Withdraw
from oms.extension.exception import CustomException

"""
ping++ 相关支付逻辑
    - 账单支付
    - 充值
    - 预充值
    - 保证金支付
    - 提现
"""

PAY_TYPE = {
    1: '账单支付',
    2: '余额充值',
    3: '保证金充值',
    4: '开发者认证支付'
}
logger = logging.getLogger('custom.charge')


class ChargeService:

    def pay(self, user_id=None, amount=0,
            channel='wx', pay_type=0,
            client_ip='127.0.0.1', extra={}):
        '''
        支付
        :params :channel 支付渠道
        :params :subject 支付主题
        :prams :body 支付内容
        :params :user_id 用户标识
        :params :amount　支付金额
        '''
        # 固定死支付金额
        amount = 1
        # TODO 支付流水号，不支持每秒并发
        ch = self.get_pingpp().Charge.create(
            order_no='cmm' + str(int(time.time())),
            channel=channel,
            amount=amount,
            subject=PAY_TYPE[pay_type],
            body=PAY_TYPE[pay_type],
            currency='cny',
            app=dict(id=settings.PINGXX_APPID),
            client_ip=client_ip,
            extra=extra
        )
        print(ch)
        return ch

    def comfirm_withdraw(self, user_id, withdraw_id):
        ''' 提现 '''
        withdraw = Withdraw.objects.\
            get(id=withdraw_id, user_id=user_id)
        if withdraw.status != 1:
            raise CustomException(10010,
                                  '【%s】状态下不允许提现' % str(withdraw.status))

        tf = self.get_pingpp().Transfer.create(
            order_no=withdraw.order_no,
            channel=withdraw.channel,
            amount=withdraw.amount,
            currency='cny',
            app=dict(id=settings.PINGXX_APPID),
            type='b2c',
            recipient=withdraw.recipient,
            extra=dict(recipient_name=withdraw.extra['recipient_name']),
            description=withdraw.description
        )
        withdraw.status = tf['status']
        withdraw.tfansfer_id = tf['id']
        withdraw._object = tf['object']
        withdraw.created = tf['created']
        withdraw.time_tfansferred = tf['time_tfansferred']
        withdraw.livemode = tf['livemode']
        withdraw.batch_no = tf['batch_no']
        withdraw.amount_settle = tf['amount_settle']
        withdraw.tfansaction_no = tf['transaction_no']
        withdraw.failure_msg = tf['failure_msg']
        withdraw.extra = tf['extra']
        withdraw.status_info = '提现成功'

        if tf.status == 'failed':
            withdraw.status_info = '提现失败'

        return withdraw

    def create_charge(self, ch, pay_type, user_id):
        ''' 根据ping++创建支付对象 '''
        charge = Charge()
        for key in ch.keys():
            setattr(charge, key, ch[key])
        charge.id = None
        charge.credential = ''
        charge.pay_type = pay_type
        charge.charge_id = ch['id']
        charge.user_id = user_id
        charge._metadata = ch['metadata']
        charge._reversed = ch['reversed']
        charge._object = ch['object']
        charge.save()
        return charge

    def get_pingpp(self):
        ''' 获取ping++实例 '''
        pingpp.api_key = settings.PINGXX_APPSECRET
        pingpp.private_key_path = os.path.join(
            os.getcwd(),
            'oms/config/pingxx/token_priv_pem.pem'
        )
        return pingpp

