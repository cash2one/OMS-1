import datetime
import logging
from django.db import transaction
from oms_server.services.fee_service import FeeService
from oms_server.services.balance_service import BalanceService
from oms_server.services.bill_service import BillService
from oms_server.services.receipt_service import ReceiptService
from oms_server.services.receipt_disbursement_service import\
    ReceiptDisbursementService
from oms_server.http_service.warehouse_service import get_warehouse_by_id
from oms_server.http_service.warehouse_service import get_all_user_warehouse
from oms_server.http_service.user_service import get_all_sub_users
from oms.extension.exception import CustomException

"""
计费系统
"""
logger = logging.getLogger('custom.billing')


class BillingService:

    def __init__(self, *args, **kwargs):
        self.fee_ser = FeeService()
        self.bill_ser = BillService()
        self.balance_ser = BalanceService()
        self.receipt_ser = ReceiptService()
        self.rd_ser = ReceiptDisbursementService()

    @transaction.atomic
    def order_billing(self, order, order_expresses):
        '''
        订单计费
            - 产生快递费用
            - 产生订单处理费用
            - 生成用仓用户账单
                - 扣减余额
            - 生成共享仓用户收入
                - 增加余额
        '''
        # 获取仓库信息(携带快递价格表)
        warehouse = get_warehouse_by_id(order.warehouse_id)
        express_amount = 0
        express_sheet_amount = 0
        express_fees = []
        sub_user = order.user_id  # 分仓用户id
        share_user = warehouse['owner_id']  # 共享仓用户id
        service = None  # 订单处理服务价格表
        # province = order.consignee_province

        for order_express in order_expresses:
            express = None
            try:
                express = [e for e in warehouse['express']
                           if e['express_code'] ==
                           order_express.logistics_code and
                           order.consignee_province in e['province']][0]
            except Exception as e:
                raise CustomException(60004, '没有找到对应的快递')
            # 快递费用
            express_fee = self.fee_ser.\
                create_express_fee(order, express, order_express)
            express_amount += express_fee.amount
            express_sheet_amount += express_fee.sheet_amount
            express_fees.append(express_fee)
        # 订单处理费用
        try:
            service = [s for s in warehouse['service']
                       if s['code'] == 20][0]
        except Exception as e:
            print(e)
            raise CustomException(60005, '没有找到订单处理费用')
        order_process_fee = self.fee_ser.\
            create_order_process_fee(order, service)
        # 用仓用户账单
        order_bill = self.bill_ser.\
            create_order_bill(express_amount=express_amount,
                              express_sheet_amount=express_sheet_amount,
                              order_process_amount=order_process_fee.amount,
                              order_process_fee=order_process_fee,
                              user_id=sub_user,
                              order=order)
        # 在用仓用户余额扣减面单费
        sub_balance = self.balance_ser.\
            deduct_balance(sub_user, express_sheet_amount)
        # 记录用仓用户流水
        disbursement = self.rd_ser.\
            disbursement(share_user, 12, express_sheet_amount)
        # 共享仓用户收入
        order_receipt = self.receipt_ser.\
            create_order_receipt(user_id=order.user_id,
                                 express_amount=express_amount,
                                 order_process_fee=order_process_fee,
                                 order=order)
        # 共享仓用户余额增加一笔订单账单费用
        share_balance = self.balance_ser.\
            add_balance(user_id=warehouse['owner_id'],
                        amount=order_receipt.amount)
        # 记录共享仓用户流水
        receipt = self.rd_ser.\
            receipt(user_id=share_user, statement_type=4,
                    amount=order_bill.amount)
        # 快递费用设置 账单 和 收入 关联
        for fee in express_fees:
            fee.order_bill = order_bill
            fee.order_receipt = order_receipt
            fee.sub_user_id = sub_user
            fee.share_user_id = share_user
            fee.save()
        order_process_fee.sub_user_id = sub_user
        order_process_fee.share_user_id = share_user
        order_process_fee.save()
        logger.info("""
            处理一笔订单发货确认申请:\n
            用仓用户{0}:\n
                产生一笔账单:{1}\n
                流水:{2}\n
                余额:{3}\n
            共享仓用户{4}:\n
                产生一笔收入:{5}
                流水:{6}
                余额:{7}\n
            """.format(sub_user, order_bill, disbursement, sub_balance,
                       share_user, order_receipt, receipt, share_balance))
        return True

    # 定时任务:每天凌晨0点
    # 需要的条件:
    # 1. 获取分仓用户以及名下的各个仓库
    # 2. 获取每个仓库下该用户的库存
    # 3. 获取库存中的所有sku长宽高,计算体积
    # 输出:
    # 1. 获取每个用户每个仓库,该时刻所有库存占的总体积
    # 2. 根据仓库的收费标准,计算费用,生成仓储费用
    # 3. 一笔费用生成一笔账单
    def storge_billing(self):
        '''
        仓储计费
        '''
        # 获取所有用仓用户和对应仓库,已经仓库下的服务
        # 量大是采用分页获取
        user_warehouses = get_all_user_warehouse()
        print(user_warehouses)
        # TODO 多线程并发处理
        # TODO 保证相互之间不影响
        for user_warehouse in user_warehouses:
            sub_user = user_warehouse['user_id']
            share_user = user_warehouse['warehouse']['owner_id']
            warehouse_id = user_warehouse['warehouse']['warehouse_id']
            warehouse_name = user_warehouse['warehouse']['warehouse_name']
            service = None
            try:
                service = [_ for _ in user_warehouse['warehouse']['service']
                           if _['code'] == 10][0]
            except Exception as e:
                logger.warning("找不到仓储服务<用仓用户:%s;共享仓用户:%s;仓库:%s>" %
                               (sub_user, share_user, warehouse_id))
                continue
            # TODO 体积计算
            storge_cost, volume = self.fee_ser.\
                caculate_storge_cost(warehouse_id, sub_user, service)
            # 创建仓储费用
            storge_fee = self.fee_ser.\
                create_storge_fee(user_id=sub_user,
                                  warehouse_id=warehouse_id, 
                                  warehouse_name=warehouse_name,
                                  amount=storge_cost,
                                  volume=volume)
            # 用仓用户增加仓储账单
            storge_bill = self.bill_ser.\
                create_storge_bill(amount=storge_fee.amount,
                                   user_id=sub_user,
                                   volume=volume,
                                   storge_fee=storge_fee,
                                   warehouse_id=warehouse_id,
                                   warehouse_name=warehouse_name)
            # 共享仓用户增加仓储收入
            storge_receipt = self.receipt_ser.\
                create_storge_receipt(user_id=share_user,
                                      amount=storge_fee.amount,
                                      storge_fee=storge_fee,
                                      warehouse_id=warehouse_id,
                                      warehouse_name=warehouse_name)
            # 共享仓用户余额增加
            share_balance = self.balance_ser.\
                add_balance(share_user, storge_fee.amount)
            # 共享仓用户收入流水
            receipt = self.rd_ser.\
                receipt(share_balance, 6, storge_fee.amount)
            logger.info("""
            结算一笔仓储费用:\n
            用仓用户{0}:\n
                产生一笔账单:{1}\n
            共享仓用户{2}:\n
                产生一笔收入:{3}
                流水:{4}
                余额:{5}\n
            """.format(sub_user, storge_bill,
                       share_user, storge_receipt, receipt, share_balance))
        return True

    @transaction.atomic
    def overdue_billing(self):
        ''' 逾期费用结算，每个月第一天 '''
        # 根据用仓用户来
        sub_users = get_all_sub_users()
        for user in sub_users:
            overdue_bill = self.bill_ser.\
                create_overdue_bill(user_id=user['user_id'])
            logger.info("""
            用仓用户{0}:结算一笔逾期费用:{1}\n
            """.format(overdue_bill.user_id, overdue_bill.amount))
        return True
