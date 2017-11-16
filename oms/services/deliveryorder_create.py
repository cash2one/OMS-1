# -*- coding: utf-8 -*-
from oms.services.cop_service import Interface
from oms_server.extension.format_utils import datetime_to_str
from oms.models.sku_item_id import SkuItemId
import logging

logger = logging.getLogger('custom.oms.deliveryorder')


class DeliveryOrder(Interface):

    def __init__(self, method='deliveryorder.create', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def sync_to_cop(self, order):
        logger.debug('*******************delivery order**********************')
        _obj = {
            'request': {
                'deliveryOrder': {
                    'deliveryOrderCode': order.id,
                    'orderType': 'JYCK',
                    'warehouseCode': order.warehouse_code,  # TODO  待确认这个参数
                    'createTime': datetime_to_str(order.created_at),
                    'placeOrderTime': datetime_to_str(order.pay_time),

                    # TODO 确定审核的时候设置了时间
                    # 'operateTime': datetime_to_str(order.operate_time),
                    'operateTime': order.operate_time,
                    'shopNick': order.store.store_name,
                    'logisticsCode': order.logistics_code,  # TODO 确定怎么选快递

                    # 'deliveryRequirements': {
                    # },

                    # TODO  仓库的地址  仓库的发货人和发货电话
                    'senderInfo': {
                        'name': 'zhangsan',
                        'mobile': '13333333333',
                        'province': '山东省',
                        'city': '青岛市',
                        'detailAddress': '黄岛区长江路街道富春江路九顶山小区207号',
                    },

                    'receiverInfo': {
                        'name': order.consignee_name,
                        'mobile': order.consignee_phone,
                        'province': order.consignee_province,
                        'city': order.consignee_city,
                        'detailAddress': order.consignee_detail,
                    },
                },
                'orderLines': {'orderLine': []}
            }
        }
        # ownerCode
        # itemCode
        # itemId
        # planQty
        # actualPrice
        for order_detail in order.order_details:
            sku_item_id = SkuItemId.objects.get(
                sku=order_detail.sku,
                warehouse_id=order.warehouse_id)
            item_id = sku_item_id.item_id
            _order_line = {
                # 2017-11-10 modify owner code to user id
                'ownerCode': str(order_detail.sku.user_id),
                # 'ownerCode': 'aircos',
                'itemCode': order_detail.sku.item_code,
                'itemId': item_id,
                'planQty': order_detail.quantity,
                'actualPrice': order_detail.price
            }
            _obj['request']['orderLines']['orderLine'].append(_order_line)
        logger.debug(_obj)
        result = self.process_message(_obj)
        logger.debug('*****************recieve response*****************')
        logger.debug(result)

        if result['response']['flag'] == 'success':
            if 'deliveryOrderId' in result['response']:
                order.delivery_order_id = result['response']['deliveryOrderId']

            # wms recieve this order
            order.wms_status = 'ACCEPT'
            order.save()
            # order history

        else:
            # TODO 失败处理
            logger.debug(result['response']['message'])
