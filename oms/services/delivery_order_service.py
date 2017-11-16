# -*- coding: utf-8 -*-
from django.db import transaction
from oms.models.order import Order
from oms.models.delivery_order_confirm import DeliveryOrderConfirm
from oms.models.order_express_material import OrderExpressMaterial
from oms.models.order_express_item import OrderExpressItem
from oms.models.order_express import OrderExpress
from oms.models.sku import Sku
from oms.services.inventory_service import InventoryService
from oms.models.order_history import OrderHistory
from oms_server.services.platforms import interface
import logging
from oms_server.services.billing_service import BillingService

logger = logging.getLogger('custom.oms.deliveryorder_confirm')


class DeliveryOrderConfirmService(object):

    @classmethod
    @transaction.atomic
    def confirm(cls, param, data):
        logger.debug(data)
        delivery_order_data = data['deliveryOrder']

        if isinstance(data['packages']['package'], list):
            packages = data['packages']['package']
        else:
            packages = [data['packages']['package']]
        # packages = data['packages']

        try:
            # 查找发货单  TODO  后续考虑是否使用deliveryOrderId
            order = Order.objects.\
                get(id=delivery_order_data['deliveryOrderCode'])
        except Exception as e:
            print(e)
            return {
                'flag': 'failure',
                'code': '10012',
                'message': 'no this order info'
            }

        try:
            # outBizCode 用于去重处理
            delivery_order_confirm = DeliveryOrderConfirm.objects.get(
                order=order,
                out_biz_code=delivery_order_data['outBizCode'])
            return {
                'flag': 'success',
                'code': '0',
                'message': ''
            }
        except Exception as e:
            delivery_order_confirm = DeliveryOrderConfirm(
                order=order,
                out_biz_code=delivery_order_data['outBizCode'],
                storageFee=float(delivery_order_data.get('storageFee', 0.0))
            )
            delivery_order_confirm.save()

            if delivery_order_data.get('status', False):
                order.wms_status = delivery_order_data['status']
            # 没有记录发票信息
            # 记录快递和包裹信息  多个快递和包裹
            # TODO 计费
            # 库存变化处理
            order_expresses = []
            for package in packages:
                order_express = OrderExpress(
                    delivery_order_confirm=delivery_order_confirm,
                    order=order,
                    logistics_code=package['logisticsCode'],
                    logistics_name=package.get('logisticsName', ''),
                    express_code=package['expressCode'],
                    # package_code=package.get('packageCode', ''),
                    length=float(package.get('length', 0.0)),
                    width=float(package.get('width', 0.0)),
                    height=float(package.get('height', 0.0)),
                    # theoretical_weight=package.get('theoreticalWeight', 0),
                    weight=float(package.get('weight', 0.0)),
                    volume=float(package.get('volume', 0.0)),
                    # invoice_No=package.get('invoiceNo', ''),
                )
                order_express.save()
                order_expresses.append(order_express)
                if 'packageMaterialList' in package:
                    if isinstance(package['packageMaterialList']['packageMaterial'], list):
                        package_material_list = package['packageMaterialList']['packageMaterial']
                    else:
                        package_material_list = [package['packageMaterialList']['packageMaterial']]
                    for package_material in package_material_list:
                        order_express_material = OrderExpressMaterial(
                            order_express=order_express,
                            order=order,
                            material_type=package_material['type'],
                            quantity=package_material['quantity'],
                        )
                        order_express_material.save()

                if isinstance(package['items']['item'], list):
                    items = package['items']['item']
                else:
                    items = [package['items']['item']]
                for item in items:
                    # 库存变化
                    # 记录数据
                    order_express_item = OrderExpressItem(
                        delivery_order_confirm=delivery_order_confirm,
                        order=order,
                        item_code=item['itemCode'],
                        item_id=item['itemId'],
                        quantity=item['quantity'],
                    )
                    order_express_item.save()

                    sku = Sku.objects.\
                        get(user_id=order.user_id, item_code=item['itemCode'])

                    InventoryService.delivery_inventory_change(
                        sku=sku,
                        quantity=item['quantity'],
                        warehouse_id=order.warehouse_id)

            # 订单保存物流单号
            express_number = ';'.join([oe.express_code for oe in order_expresses])
            order.express_number = express_number
            order.save()
            
            # TODO 启动电商平台回传物流信息
            platform_name = order.store.platform.name
            store_detail = {
                "access_token": order.store.access_token
            }
            for package in packages:
                if isinstance(package['items']['item'], list):
                    items = package['items']['item']
                else:
                    items = [package['items']['item']]
                skus_param = []
                for item in items:
                    sku = {
                        "item_code": item["itemCode"],
                        "item_sku_id": item["itemId"]
                        # "item_sku_id": item["sku_id"]
                    }
                    skus_param.append(sku)

                logger.debug('%s: order.order_code = %s' % (platform_name, order.order_code))
                logger.debug('%s: express_code = %s' % (platform_name, package['logisticsCode']))
                logger.debug('%s: deliver_no = %s' % (platform_name, package['expressCode']))
                success, error_msg = interface.order_delivery(
                    platform_name, store_detail, order.order_code,
                    package['logisticsCode'], package['expressCode'])
                if error_msg:
                    logger.debug('%s: order_delivery failed, %s' % (platform_name, error_msg))
                else:
                    logger.info('%s: order_delivery success' % platform_name)

            # TODO 计费

            # TODO 计费, 同步
            # billing_success = BillingService().\
            #     order_billing(order=order, order_expresses=order_expresses)
            # if not billing_success:
            #     pass

            # 记录订单处理历史
            order_history = OrderHistory(
                order=order,
                operator='warehouse',
                action='delivery',
                is_system=True,
            )
            order_history.save()
            order.wms_status = delivery_order_data['status']
            logger.debug('order %s status is %s now' % (order.id, order.wms_status))
            order.save()
            logger.debug('delivery order confirm ok')
            # 返回结果
            return {
                'flag': 'success',
                'code': '0',
                'message': ''
            }
