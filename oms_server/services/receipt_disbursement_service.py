import logging
from oms.models.receipt_disbursement_statement import\
    ReceiptDisbursementStatement

"""
收支明细相关逻辑
"""

logger = logging.getLogger('custom.receipt_disbursement')
STATEMENT_TYPE = {
    1: '充值',
    2: '预充值',
    3: '保证金',
    4: '订单收入',
    5: '账单收入',
    6: '仓储收入',
    # 支出
    11: '账单支出',
    12: '面单费用支出',
    13: '提现',
    14: '开发者认证支付'
}


class ReceiptDisbursementService:

    def list_receipt_disbursement(self, user_id,
                                  is_receipt=None, statement_type=0):
        '''
        收支明细列表
        :params :is_receipt 默认为None, True表示收入, False表示支出
        :params :statement_type 收支类型
        '''
        pass

    def receipt(self, user_id, statement_type, amount):
        ''' 添加一笔收入 '''
        is_receipt = 0 < statement_type < 10
        receipt = ReceiptDisbursementStatement(
            user_id=user_id,
            is_receipt=is_receipt,
            amount=amount,
            statement_type=statement_type
        )
        receipt.save()
        logger.info('用户{0}：添加一笔{1}收入:{2}'.
                    format(user_id, STATEMENT_TYPE[statement_type], amount))
        return receipt

    def disbursement(self, user_id, statement_type, amount):
        ''' 添加一笔支出 '''
        is_receipt = 0 < statement_type < 10
        disbursement = ReceiptDisbursementStatement(
            user_id=user_id,
            is_receipt=is_receipt,
            amount=amount,
            statement_type=statement_type
        )
        disbursement.save()
        logger.info('用户{0}：添加一笔{1}支出:{2}'.
                    format(user_id, STATEMENT_TYPE[statement_type], amount))
        return disbursement
