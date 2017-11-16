# -*- coding: utf-8 -*-
from oms.services.cop_service import Interface
import logging

logger = logging.getLogger('custom.oms.order_cancel')


class OrderCancel(Interface):

    def __init__(self, method='taobao.qimen.order.cancel', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def sync_to_cop(self, order_info):
        # warehouseCode String 必须 W1234仓库编码(统仓统配等无需ERP指定仓储编码的情况填OTHER)
        # ownerCode String 可选 H1234货主编码
        # orderCode String 必须 O1234单据编码
        # orderId String 可选 WQ1234仓储系统单据编码
        # orderType String 可选 JYCK单据类型(JYCK=一般交易出库单;
        #     HHCK= 换货出库;BFCK=补发出库;PTCK=普通出库单;DBCK=调拨出库;
        #     B2BRK=B2B入库;B2BCK=B2B出库;QTCK=其他出库;SCRK=生产入库;
        #     LYRK=领用入库;CCRK=残次品入库;CGRK=采购入库;DBRK= 调拨入库;
        #     QTRK=其他入库;XTRK= 销退入库;THRK=退货入库;HHRK= 换货入库;
        #     CNJG= 仓内加工单;CGTH=采购退货出库单)
        # cancelReason String 可选 已经退货取消原因
        _obj = {
            'request': {
                'warehouseCode': order_info['warehouse_code'],
                'orderCode': order_info['order_code'],
                'ownerCode': order_info['owner_code'],
                'orderId': order_info['order_id'],
                'orderType': order_info['order_type'],
                'cancelReason': order_info['cancel_reason'],
            }
        }
        return self.process_message(_obj)

    def delivery_order_cancel(self, order, reason='refunded'):
        order_info = {
            'warehouse_code': order.warehouse_code,
            'owner_code': order.user_id,
            'order_code': order.id,
            'order_id': order.delivery_order_id,
            'order_type': 'JYCK',
            'cancel_reason': reason,
        }

        result = self.sync_to_cop(order_info)

        if result['response']['flag'] == 'success':
            order.order_status = 50
            order.wms_status = 'CANCELED'
            order.save()
            # TODO order history
        else:
            logger.debug(result)


class DeliveryOrderCance(OrderCancel):
    def __init__(self, method='taobao.qimen.order.cancel', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def delivery_order_cancel(self, order, reason='refunded'):
        order_info = {
            'warehouse_code': order.warehouse_code,
            'owner_code': order.user_id,
            'order_code': order.id,
            'order_id': order.delivery_order_id,
            'order_type': 'JYCK',
            'cancel_reason': reason,
        }

        result = self.sync_to_cop(order_info)

        if result['response']['flag'] == 'success':
            order.order_status = 50
            order.wms_status = 'CANCELED'
            order.save()
            # TODO order history
        else:
            logger.debug(result)


class EntryOrderCancel(OrderCancel):
    def __init__(self, method='order.cancel', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def entry_order_cancel(self, stock_in_order, reason):
        order_info = {
            'warehouse_code': stock_in_order.warehouse_code,
            'owner_code': stock_in_order.user_id,
            'order_code': stock_in_order.id,
            'order_id': stock_in_order.entry_order_id,
            'order_type': 'CGRK',
            'cancel_reason': reason,
        }

        result = self.sync_to_cop(order_info)

        if result['response']['flag'] == 'success':
            # order.order_status = 50
            stock_in_order.stock_in_status = 'CANCELED'
            stock_in_order.save()
            # TODO order history
        else:
            logger.debug(result)



class StockOutCancel(OrderCancel):
    pass
