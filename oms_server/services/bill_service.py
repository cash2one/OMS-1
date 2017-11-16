import datetime
import logging
from django.db.models import Sum, Count
from django.core.paginator import Paginator
from oms.models import OverdueBill
from oms.models.order_bill import OrderBill
from oms.models.storge_bill import StorgeBill
from oms.extension.exception import CustomException
from oms_server.services.charge_service import ChargeService


"""
用仓用户账单相关逻辑
    - 仓储费
    - 面单费用
    - 订单处理费
"""
logger = logging.getLogger('custom.bill')


class BillService:

    def bill_statistics(self, user_id):
        '''
        账单统计
        1.总账单
        2.待支付账单
            - 仓库费用
                - 仓储费
                - 快递费
                - 订单处理费
            - 逾期费用
        3.已支付账单
        '''
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        order_bill = OrderBill.objects.\
            only('amount', 'express_sheet_amount', 'paid').\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month)
        storge_bill = StorgeBill.objects.\
            only('amount', 'paid').\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month)
        # 订单账单总费用
        o_amount = sum([ob.amount for ob in order_bill])
        # 订单账单结算费用
        o_settle_amount = sum([_.express_sheet_amount
                               for _ in order_bill])
        # 订单账单未结算费用
        o_unsettle_amount = sum([_.unsettle_amount
                                for _ in order_bill
                                if _.paid is False])
        # TODO 性能优化,迭代三次改为一次
        s_amount = sum([sb.amount for sb in storge_bill])
        s_settle_amount = sum([_.amount for _ in storge_bill
                               if _.paid is True])
        s_unsettle_amount = sum([_.amount for _ in storge_bill
                                 if _.paid is False])
        # TODO 应该将创建时间 和 账单时间 分开
        overdue_amount = OverdueBill.objects.\
            only('amount').\
            filter(user_id=user_id,
                   paid=False,
                   year=year,
                   month=month) or 0
        if overdue_amount:
            overdue_amount = overdue_amount[0].amount
        result = {
            'total_bill_amount': o_amount + s_amount + overdue_amount,
            'settle_bill_amount': o_settle_amount + s_settle_amount,
            'unsettle_bill_amount': o_unsettle_amount + s_unsettle_amount +
            overdue_amount
        }
        return result

    def total_bill_statistics(self, user_id, year, month):
        '''
        总账单统计
            - 根据仓库汇总
        '''
        # 聚合
        order_bill = OrderBill.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(express_amount=Sum('express_amount'),
                     express_sheet_amount=Sum('express_sheet_amount'),
                     amount=Sum('amount'),
                     process_amount=Sum('order_process_amount'),
                     order_counts=Count('id')).\
            values('order_counts', 'amount',
                   'express_amount', 'process_amount',
                   'warehouse_id', 'warehouse_name')
        # 仓储费
        storge_bill = StorgeBill.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(storge_days=Count('id'),
                     storge_amount=Sum('amount')).\
            values('storge_amount', 'storge_days',
                   'warehouse_id', 'warehouse_name')
        overdue_bill = OverdueBill.objects.\
            filter(user_id=user_id,
                   paid=False,
                   year=year, month=month).\
            values('amount')
        
        return self.aggregation_bill(order_bill=order_bill,
                                     storge_bill=storge_bill,
                                     overdue_bill=overdue_bill)

    def unsettle_bill_statistics(self, user_id):
        '''
        待支付账单(只显示当月)
            根据仓库汇总
            逾期账单
            未结算订单账单
                - paid == False
                - created_at__year == now_year
                - created_at__year === now_month
                - unsettle_amount(未结算金额)
        '''
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        # 订单账单未结算金额
        order_bill = OrderBill.objects.\
            filter(user_id=user_id,
                   paid=False,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(express_amount=Sum('express_amount') -
                     Sum('express_sheet_amount'),
                     amount=Sum('unsettle_amount'),
                     process_amount=Sum('order_process_amount'),
                     order_counts=Count('id')).\
            values('warehouse_id', 'warehouse_name',
                   'express_amount', 'process_amount',
                   'order_counts', 'amount')
        print(order_bill)
        # 仓储费未结算金额
        storge_bill = StorgeBill.objects.\
            filter(user_id=user_id,
                   paid=False,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(storge_days=Count('id'),
                     storge_amount=Sum('amount')).\
            values('storge_amount', 'storge_days',
                   'warehouse_id', 'warehouse_name')
        # 逾期费用
        overdue_bill = OverdueBill.objects.\
            filter(user_id=user_id,
                   paid=False,
                   year=year, month=month).\
            values('amount')
        return self.aggregation_bill(order_bill=order_bill,
                                     storge_bill=storge_bill,
                                     overdue_bill=overdue_bill)

    def settle_bill_statistics(self, user_id):
        ''' 已支付账单统计(当月) '''
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        # 订单账单已结算金额
        order_bill = OrderBill.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(total_amount=Sum('express_sheet_amount'),
                     total_count=Count('id')).\
            values('warehouse_id', 'warehouse_name',
                   'total_amount', 'total_count')
        # 仓储费已结算金额
        storge_bill = StorgeBill.objects.\
            filter(user_id=user_id,
                   paid=True,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(total_day=Count('id'),
                     total_amount=Sum('amount')).\
            values('total_amount', 'total_day',
                   'warehouse_id', 'warehouse_name')
        return order_bill, storge_bill
    
    def details(self, user_id, start_time, end_time,
                bill_type=1, page_size=10):
        '''
        账单明细
        :params :bill_type 1:发货账单 2:仓储账单
        :params :
        '''
        if int(bill_type) == 1:
            query_set = OrderBill.objects.\
                filter(user_id=user_id,
                       created_at__range=(start_time, end_time))
            paginator = Paginator(query_set, per_page=page_size)
            return paginator
        elif int(bill_type) == 2:
            query_set = StorgeBill.objects.\
                filter(user_id=user_id,
                       created_at__range=(start_time, end_time))
            return Paginator(query_set, per_page=page_size)
        else:
            raise CustomException(40004, '不支持的账单类型')
        return None

    def create_order_bill(self, express_amount, express_sheet_amount,
                          order_process_amount,
                          order_process_fee,
                          user_id,
                          order):
        '''
        创建订单账单
        :params :express_fee(many)
        :params :order_process_fee
        '''
        amount = express_amount + order_process_amount
        unsettle_amount = amount - express_sheet_amount
        order_bill = OrderBill(
            paid=False,
            express_amount=express_amount,
            express_sheet_amount=express_sheet_amount,
            order_process_amount=order_process_amount,
            unsettle_amount=unsettle_amount,
            amount=amount,
            order_process_fee=order_process_fee,
            user_id=user_id,
            order_id=order.id,
            order_code=order.order_code,
            warehouse_id=order.warehouse_id,
            warehouse_name=order.warehouse_name
        )
        order_bill.save()
        return order_bill

    def create_storge_bill(self, amount, user_id, storge_fee,
                           warehouse_id, warehouse_name, volume):
        ''' 创建存储账单 '''
        storge_bill = StorgeBill(
            amount=amount,
            paid=False,
            volume=volume,
            user_id=user_id,
            warehouse_id=warehouse_id,
            storge_fee_id=storge_fee.id,
            warehouse_name=warehouse_name
        )
        storge_bill.save()
        return storge_bill

    def create_overdue_bill(self, user_id):
        ''' 创建逾期费用账单 '''
        now = datetime.date.today()
        now_year = now.year
        now_month = now.month
        last = now.replace(day=1) - datetime.timedelta(1)
        last_year = last.year
        last_month = last.month

        order_bills = OrderBill.objects.\
            filter(user_id=user_id,
                   paid=False,
                   created_at__year=last_year,
                   created_at__month=last_month)
        order_bill_amount = sum([ob.amount for ob in order_bills])
        storge_bills = StorgeBill.objects.\
            filter(user_id=user_id,
                   paid=False,
                   created_at__year=last_year,
                   created_at__month=last_month)
        storge_bill_amount = sum([sb.amount for sb in storge_bills])
        overdue_bill = OverdueBill.objects.\
            filter(user_id=user_id, paid=False, is_deleted=False)  # 讲道理最多只能有一个
        overdue_bill_amount = 0
        if len(overdue_bill) > 1:
            logger.error("""
                用户:<{0}>有{1}笔逾期账单！！！
            """.format(user_id, len(overdue_bill)))
        elif len(overdue_bill) == 1:
            overdue_bill_amount = overdue_bill[0].amount
        amount = order_bill_amount + storge_bill_amount + overdue_bill_amount
        # TODO 之前的逾期账单怎么处理？paid=True? is_deleted=True?结算状态?
        if not amount:
            overdue_bill = OverdueBill(
                user_id=user_id,
                amount=amount,
                year=now_year,
                month=now_month,
                paid=False,
            )
            overdue_bill.save()
            return overdue_bill
        else:
            return None

    # TODO 赶工,优化代码
    def aggregation_bill(self, order_bill=None,
                         storge_bill=None, overdue_bill=None):
        result = {}
        warehouses = order_bill
        result['warehouses'] = list(warehouses)
        # print("===========================")
        # print(order_bill)
        # print(storge_bill)
        # print(overdue_bill)
        # print("============================")
        overdue_days = datetime.date.today().day
        for sb in storge_bill:
            for warehouse in warehouses:
                if warehouse['warehouse_id'] == sb['warehouse_id']:
                    warehouse['storge_amount'] = sb['storge_amount']
                    warehouse['storge_days'] = sb['storge_days']
                    warehouse['amount'] += sb['storge_amount']
                    break
            else:
                result.setdefault('warehouses', [])
                sb['amount'] = sb['storge_amount']
                result['warehouses'].append(sb)
        if overdue_bill:
            result['overdue_amount'] = overdue_bill[0]
            result['overdue_days'] = overdue_days
        result['warehouses'] =\
            sorted(result['warehouses'], key=lambda x: x['amount'], reverse=True)
        return result

    def pay(self, user_id, params):
        ''' 待支付账单支付 '''
        now = datetime.datetime.now()
        year = now.year
        month = now.month
        _total_amount = params['amount']  # 支付账单的总额
        channel = params['channel']
        client_ip = params.get('client_ip', '127.0.0.1')
        extra = {}
        if channel == 'alipay_pc_direct':
            extra = dict(success_url=params['success_url'])
        total_amount = 0
        order_bills = []  # 订单账单
        storge_bills = []  # 仓储账单
        overdue_bill = None  # 逾期账单
        if 'warehouses' in params.keys():
            for warehouse in params['warehouses']:

                warehouse_id = warehouse['warehouse_id']
                _express_amount = warehouse.get('express_amount', 0)
                _process_amount = warehouse.get('process_amount', 0)
                _storge_amount = warehouse.get('storge_amount', 0)
                _amount = warehouse['amount']

                # 找到该仓库该用户所有的未支付订单账单
                _order_bills = OrderBill.objects.\
                    filter(warehouse_id=warehouse_id,
                           user_id=user_id,
                           created_at__year=year,
                           created_at__month=month,
                           paid=False)
                express_amount = sum([_.express_amount - _.express_sheet_amount
                                     for _ in _order_bills])
                process_amount = sum([_.order_process_amount
                                      for _ in _order_bills])
                order_bill_amount = sum([_.unsettle_amount
                                        for _ in _order_bills])
                _storge_bills = StorgeBill.objects.\
                    filter(warehouse_id=warehouse_id,
                           user_id=user_id,
                           created_at__year=year,
                           created_at__month=month,
                           paid=False)
                storge_bill_amount = sum([_.amount for _ in _storge_bills])
                amount = order_bill_amount + storge_bill_amount
                # 比较费用
                self.compair_amount(_express_amount, express_amount, '快递')
                self.compair_amount(_process_amount, process_amount, '处理')
                self.compair_amount(_storge_amount, storge_bill_amount, '仓储')
                self.compair_amount(_amount, amount, '')
                order_bills.extend(_order_bills)
                storge_bills.extend(_storge_bills)
                total_amount += amount
                
            # 在之前返回前端待支付的金额，和现在支付结算的期间产生的新的未支付账单怎么处理？
            # 现在假设不存在这部分账单
        if 'overdue' in params.keys():
            overdue_bill = OverdueBill.objects.\
                filter(user_id=user_id,
                       paid=False,
                       year=year,
                       month=month)
            if not overdue_bill:
                raise CustomException(40005, '逾期费用为0')
            total_amount += overdue_bill[0].amount
        self.compair_amount(_total_amount, total_amount, '总')
        # ping++支付
        charge_ser = ChargeService()
        ch = charge_ser.pay(user_id=user_id, amount=total_amount,
                            extra=extra,
                            channel=channel, pay_type=2, client_ip=client_ip)
        charge = charge_ser.create_charge(ch=ch, pay_type=2, user_id=user_id)
        # 可以根据charge_id 判断该账单是否支付过
        for ob in order_bills:
            ob.charge_id = charge.id
            ob.save()
        for sb in storge_bills:
            sb.charge_id = charge.id
            sb.save()
        if overdue_bill:
            overdue_bill.charge_id = charge.id
            overdue_bill.save()
        return ch

    def compair_amount(self, a, b, extra):
        if a != b:
            raise CustomException(10016, '<%s>费用不一致' % extra)