from django.db.models import Sum, Count
from django.core.paginator import Paginator
from oms.models.order_receipt import OrderReceipt
from oms.models.storge_receipt import StorgeReceipt
from oms.extension.exception import CustomException

"""
共享仓用户收入相关逻辑
"""


class ReceiptService:

    def receipt(self, user_id, year, month):
        ''' 总收入 '''
        order_amount = OrderReceipt.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            aggregate(Sum('amount'))
        order_amount = order_amount['amount__sum'] or 0
        storge_amount = StorgeReceipt.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            aggregate(Sum('amount'))
        storge_amount = storge_amount['amount__sum'] or 0
        amount = order_amount + storge_amount
        return amount

    def receipt_statistics(seld, user_id, year, month):
        ''' 收入详情 '''
        order_receipt = OrderReceipt.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(order_counts=Count('id'),
                     process_amount=Sum('order_process_amount'),
                     express_amount=Sum('express_amount')).\
            values('order_counts', 'process_amount',
                   'express_amount', 'warehouse_id',
                   'warehouse_name')
        storge_receipt = StorgeReceipt.objects.\
            filter(user_id=user_id,
                   created_at__year=year,
                   created_at__month=month).\
            values('warehouse_id').\
            annotate(total_days=Count('id'),
                     storge_amount=Sum('amount')).\
            values('total_days', 'storge_amount',
                   'warehouse_id', 'warehouse_name')
        return seld.aggregation_receipt(order_receipt=order_receipt,
                                        storge_receipt=storge_receipt)

    def details(self, user_id, start_time, end_time,
                receipt_type=1, page_size=10):
        '''
        收入明细
        :params :receipt_type 1:订单收入 2:仓储收入
        '''
        print(start_time, end_time)
        if int(receipt_type) == 1:
            query_set = OrderReceipt.objects.\
                filter(user_id=user_id,
                       created_at__range=(start_time, end_time))
            paginator = Paginator(query_set, per_page=page_size)
            return paginator
        elif int(receipt_type) == 2:
            query_set = StorgeReceipt.objects.\
                filter(user_id=user_id,
                       created_at__range=(start_time, end_time))
            return Paginator(query_set, per_page=page_size)
        else:
            raise CustomException(40007, '不支持的收入类型')
        return None

    def create_order_receipt(self, user_id, express_amount,
                             order_process_fee,
                             order):
        ''' 创建一笔订单收入概览 '''
        amount = express_amount + order_process_fee.amount
        order_receipt = OrderReceipt(
            amount=amount,
            express_amount=express_amount,
            order_process_amount=order_process_fee.amount,
            order_process_fee=order_process_fee,
            user_id=user_id,
            order_id=order.id,
            warehouse_id=order.warehouse_id,
            warehouse_name=order.warehouse_name
        )
        order_receipt.save()
        return order_receipt

    def create_storge_receipt(self, user_id, amount, storge_fee,
                              warehouse_id, warehouse_name):
        ''' 创建一笔仓储收入 '''
        storge_receipt = StorgeReceipt(
            amount=amount,
            user_id=user_id,
            storge_fee_id=storge_fee.id,
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name
        )
        storge_receipt.save()
        return storge_receipt

    # TODO 赶工,优化代码
    def aggregation_receipt(self, order_receipt=None,
                            storge_receipt=None):
        result = {}
        warehouses = order_receipt
        for sb in storge_receipt:
            for warehouse in warehouses:
                if warehouse['warehouse_id'] == sb['warehouse_id']:
                    warehouse['storge_amount'] = sb['storge_amount']
                    warehouse['storge_days'] = sb['storge_days']
                    break
            else:
                warehouse.append(sb)
        result['warehouses'] = warehouses
        return result
