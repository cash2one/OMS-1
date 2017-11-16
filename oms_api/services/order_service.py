# -*- coding:utf-8 -*-
import time
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Prefetch
from oms.models.order import Order
from oms.models.sku import Sku
from oms.models.store import Store
from oms.models.activity_sku import ActivitySku
from oms.models.activity_rule import ActivityRule
from oms.models.order_detail import OrderDetail
from oms.models.sku_warehouse import SkuWarehouse
from oms.models.split_combine_order import SplitCombineOrder
from oms.extension.exception import CustomException
from oms_api.services.inventory_service import InventoryService
from oms.services import inventory_service
from oms.services.id_generation_service import IdGenerationService
from oms_server.http_service.warehouse_service import get_warehouse_by_id
from oms.services.deliveryorder_create import DeliveryOrder
from oms.services.order_cancel import OrderCancel
from oms_server.http_service.user_service import get_user_info
import logging

logger = logging.getLogger('custom.oms_api.order')


class OrderService(object):

    # 订单审核接口，用于前端人工处理订单后的检查工作
    # 包括库存确认，地址校验，仓库路由
    @classmethod
    def order_Examination(cls, order):

        # 地址校验
        if not cls.check_address(order):
            raise CustomException('20002', '地址校验不通过')

        order_diff = cls.check_stock_change(order)

        # 库存校验，包括锁定库存的修改，比如商品修改数量的处理
        # 怎么处理原来没有的商品现在增加了的场景
        if not cls.check_stock(order_diff):
            raise CustomException('20001', '库存不足')
        # 仓库校验， 包括仓库库存。 如果没有仓库，进行路由和拆单处理(if need)
        if order['warehouse_id']:
            if not cls.check_warehouse_stock(order['order_detail'], order['warehouse_id']):
                raise CustomException('20004', '目的仓库库存不足')
        else:
            cls.route(order)

        # 订单状态修改  已审核

        # 跟wms交互

        return {'success': True}

    @classmethod
    def check_address(cls, order):
        keys_zh = r'[^\u4e00-\u9fa5^A-Za-z_0-9,\,\:\.\x00,\，\：\ \。\#]'
        addr = str(order['consignee_detail'])
        if (addr == ""):
            return False
        return True

    # order_dicts的
    @classmethod
    def check_stock_change(cls, order):
        order_dicts = {order_detail['sku_id']: order_detail['quantity'] for order_detail in order['order_details']}
        order_id = order['order_id']
        order_detail_list = OrderDetail.objects.filter(order__id=order_id)
        order_diff = {order_detail.sku.id: int(order_dicts.get(order_detail.sku.id, 0)) - order_detail.quantity for order_detail in order_detail_list}
        for (key, value) in order_dicts:
            if key not in order_diff:
                order_diff[key] = value
        return order_diff

    @classmethod
    def check_stock(cls, order_diff):
        for (key, value) in order_diff:
            sku_info = InventoryService.sku_get_warehouse_by_id(key)
            if not sku_info['result']['is_exist']:
                return False
            if sku_info['result']['available_count'] < value:
                return False
        return True

    @classmethod
    def check_warehouse_stock(cls, order_detail_list, warehouse_id):
        for order_detail in order_detail_list:
            try:
                sku_warehouse = SkuWarehouse.objects.get(
                    sku__id=order_detail['sku_id'], warehouse__id=warehouse_id)
                if int(order_detail['quantity']) > sku_warehouse.available_quantity:
                    return False
            except Exception as e:
                raise CustomException('10001', str(e))
        return True

    @classmethod
    def set_warehouse(cls, order_id, warehouse_id):
        try:
            order = Order.objects.get(id=order_id)
            # TODO 判断仓库是否存在
            # warehouse = Warehouse.objects.get(id=warehouse_id)
            # if not warehouse:
            #     raise CustomException('10003', '仓库不存在')
            order.warehouse_id = warehouse_id
            # 选择完仓库的时候已经锁定库存了，所以此处不再校验仓库库存
            order.save()
            # TODO 是在这个时候做发货单创建吗？
            return {'success': True}
        except Exception as e:
            return {'success': False}

    @classmethod
    def find_order(cls, store_id, order_mark):
        orders = Order.objects.\
            filter(store__id=store_id, order_mark=order_mark)
        order_list = [cls.order_info(order) for order in orders]
        return order_list

    @classmethod
    def get_order_detail(cls, order):
        order_details = OrderDetail.objects.filter(order=order)
        order_detail = [{
            'is_exist': detail.sku.is_exist,
            'order_detail_id': detail.id,
            'item_code': detail.sku.item_code,
            'sku_id': detail.sku.id,
            'order_id': order.id,
            'quantity': detail.quantity,
            'is_gift': detail.is_gift,
            'price': detail.price,
            'total_price': detail.total_price
        } for detail in order_details]
        return order_detail

    @classmethod
    def order_info(cls, order):
        order_detail = cls.get_order_detail(order)
        return {
            'quantity': order.quantity,
            'consignee_phone': order.consignee_phone,
            'refund_status_ori': order.refund_status_ori,
            'express_number': order.express_number,
            'total_price': order.total_price,
            'buyer_note': order.buyer_note,
            'store_id': order.store_id,
            'goods_price': order.goods_price,
            'seller_note': order.user_note,
            'platform_id': order.store.platform.id,
            'consignee_country': order.consignee_country,
            'consignee_detail': order.consignee_detail,
            'order_type': order.order_type,
            'express_fee': order.express_fee,
            'status': order.order_status,
            'express_note': order.express_note,
            'consignee_city': order.consignee_city,
            'order_status_info': order.order_status_info,
            'order_code': order.order_code,
            'order_id': order.id,
            'consignee_area': order.consignee_area,
            'order_mark': order.order_mark,
            'pay_time': order.pay_time,
            'consignee_name': order.consignee_name,
            'order_details': order_detail,
            'mark_reason': order.mark_reason,
            'consignee_province': order.consignee_province,
            'status_ori': order.status_ori,
            'express_type': order.express,
            'store_is_auto_check': order.store.auto_check,
            'user_id': order.user_id,
            'add_time': order.add_time
        }

    # 构建一个订单
    @classmethod
    def create_order(cls, order):
        logger.debug('==================================')
        logger.debug(order)
        logger.debug('==================================')
        o = Order()
        # if order.get('order_id', False):
        #     o.id = order['order_id']

        # 按照规则生成order的id
        o.id = IdGenerationService.generate_order_id()

        o.consignee_country = order['consignee_country']
        store_id = order['store_id']
        user_id = order['user_id']
        user_info = get_user_info(user_id)
        o.user_name = user_info['nickname']
        o.user_id = user_id
        try:
            store = Store.objects.get(id=store_id)
        except:
            raise CustomException('10001', '店铺不存在')
        else:
            o.store = store
        order_status_info = order.get('order_status_info', '')
        if order_status_info:
            o.order_status_info = order_status_info
        else:
            o.order_status_info = '10'
        o.order_status = order.get('order_status', '10')
        o.mark_reason = order['mark_reason']
        o.express_note = order['express_note']
        o.buyer_note = order['buyer_note']
        o.goods_price = order['goods_price']
        o.express_type = order['express_type']
        o.status_ori = order['status_ori']
        o.quantity = order['quantity']
        o.consignee_detail = order['consignee_detail']
        o.express_fee = order['express_fee']
        o.consignee_country = order['consignee_country']
        o.order_code = order['order_code']
        o.consignee_area = order['consignee_area']
        o.refund_status_ori = order['refund_status_ori']
        o.total_price = order['total_price']
        o.express_number = order['express_number']
        o.consignee_phone = order['consignee_phone']
        o.consignee_city = order['consignee_city']
        o.consignee_province = order['consignee_province']
        o.consignee_name = order['consignee_name']
        o.pay_time = order['pay_time']
        o.add_time = order['add_time']
        if order.get('warehouse_id', False):
            o.warehouse_id = order['warehouse_id']
        o.created_at = time.strftime(
            '%Y-%m-%d %H:%M:%S',
            time.localtime(time.time()))
        o.save()
        for order_detail in order['order_details']:
            item_code = order_detail['item_code']
            sku = Sku.objects.get(item_code=item_code, user_id=user_id)
            od = OrderDetail()
            # od.sku_id = sku.id
            od.total_price = order_detail['total_price']
            # od.order_id = order_detail['order_id']
            od.order = o
            od.sku = sku
            od.price = order_detail['price']
            # od.order_detail_id = order_detail['order_detail_id']
            od.quantity = order_detail['quantity']
            od.save()
        return {'order_id': o.id}

    # 设置订单标签
    @classmethod
    def set_mark_tag(cls, order_code, store_id, reason, mark):
        order = Order.objects.get(order_code=order_code, store__id=store_id)
        order.order_mark = int(mark)
        order.mark_reason = reason
        order.save()
        return {}

    # 获取订单详情
    @classmethod
    def get_detail(cls, order_code, store_id):
        try:
            order = Order.objects.\
                get(order_code=order_code, store__id=store_id)
            order_info = cls.order_info(order)
        except Exception as e:
            print(e)
            return {}
        else:
            return order_info

    # 设置订单状态
    @classmethod
    def set_status_ori(cls, order_code, store_id,
                       status_ori, refund_status_ori):
        order = Order.objects.\
            get(order_code=order_code, store__id=store_id)
        refund_status_oris = int(refund_status_ori)
        if refund_status_oris in (0, 1, 2, -1):
            order.status_ori = status_ori
            order.refund_status_ori = refund_status_oris
            if refund_status_oris == 1:
                cls.refund(order)
            order.save()
            return {}
        else:
            raise CustomException('20001', '订单状态不合法')

    # 设置订单状态(new)
    @classmethod
    def set_status(cls, order_code, store_id, status):
        # TODO temp
        order = Order.objects.\
             get(order_code=order_code, store__id=store_id)
        order_details = OrderDetail.objects.\
            filter(order=order, is_deleted=False).\
            select_related('sku')
        order = Order.objects.\
            prefetch_related(
                Prefetch('order_detail', queryset=order_details,
                         to_attr='order_details')
            ).\
            select_related('store').\
            get(order_code=order_code, store__id=store_id)

        status = int(status)
        if status in (10, 20, 30, 40):
            order.order_status = status
        if status == 20:
            logger.debug('order auto approved')
            order.order_status = status
            order.operate_time = time.strftime(
                '%Y-%m-%d %H:%M:%S',
                time.localtime(time.time()))
            if not order.is_splited:
                logger.debug('send to wms, order_id : ' + order.id)
                order = cls.set_warehouse_info(order)
                # TODO  custom_id  warehouse_id
                DeliveryOrder(custom_id=order.warehouse_id, id=order.id).sync_to_cop(order)
            order.save()
        elif status in (10, 30, 40):
            order.order_status = status
            order.save()
            return {}
        else:
            raise CustomException('20001', '订单状态不合法')

    @classmethod
    def add_skus(cls, datas):
        for od_data in datas:
            try:
                order = Order.objects.get(id=od_data['order_id'])
                sku = Sku.objects.get(id=od_data['sku_id'])
                order_detail = OrderDetail.objects.get(order=order, sku=sku)
                order_detail.quantity += int(od_data['quantity'])
                order.quantity += int(od_data['quantity'])
                order_detail.is_gift = od_data['is_gift']
                order_detail.save()
                order.save()
            except Exception as e:
                od = OrderDetail()
                od.order = order
                od.sku = sku
                od.item_code = od_data['item_id']
                od.price = od_data['price']
                od.quantity = od_data['quantity']
                order.quantity += int(od_data['quantity'])
                od.total_price = od_data['total_price']
                od.is_gift = od_data['is_gift']
                od.save()
                order.save()
        return {}

    @classmethod
    def split_order(cls, order_id, split_orders):
        order = Order.objects.get(id=order_id)
        order.is_splited = True
        # 设置状态为已拆单
        order.order_status = 70
        inventory_service.InventoryService.clear_locked_inventory(order_id)
        split_order_ids = []
        for split_order in split_orders:
            result = cls.create_order(split_order)
            inventory_service.InventoryService.lock_inventory(result['order_id'])
            inventory_service.InventoryService.lock_inventory(result['order_id'], split_order['warehouse_id'])
            # if result['success']:
            split_order_ids.append(result['order_id'])
        sub_order_sequence = 0
        for id in split_order_ids:
            sub_order_sequence = sub_order_sequence + 1
            split_order = SplitCombineOrder(
                sub_order_sequence=sub_order_sequence,
                new_order=id,
                original_order=order.id,
                is_splited=True)
            split_order.save()
        order.save()
        return {'success': True}

    @classmethod
    def get_orders_store_status(cls, store, status):
        orders = Order.objects. \
            filter(store=store). \
            filter(order_status=status). \
            filter(is_locked=False)
        return orders
        # 订单加工:满赠
        # 订单来源: 是一个订单队列
        # 订单去处: 是一个订单中心表
        # TODO
        # 事件驱动订单状态的转变: 状态机
        # @classmethod
        # def handle(cls, order):

        # TODO
        # 判断订单是否在电商平台处理过了
        #
        # 没有处理过的话，做赠品处理
        # 查找订单包含的商品id 和件数和价格
        product_infoes = {order_detail.product_id:
                          (order_detail.quantity, order_detail.price)
                          for order_detail in order.order_details}
        # 获取订单里商品相关的活动
        activity_products = ActivitySku.objects. \
            filter(product_id__in=list(product_infoes.keys()),
                   activity__activity_type=2,  # 满赠活动商品筛选
                   activity__is_expired=False,
                   activity__is_invalid=False)
        activities = {}
        # 查看所有的活动和活动下的商品信息
        # 当前逻辑 一个商品只能参与一个活动
        for activity_product in activity_products:
            activities.setdefault(activity_product.activity_id, {})
            activities[activity_product.activity_id]. \
                setdefault('activity',
                           Activity.objects.
                           get(id=activity_product.activity_id))
            activities[activity_product.activity_id].setdefault('items', [])
            activities[activity_product.activity_id]['items']. \
                append(product_infoes.pop(activity_product.product_id))
        # 计算满赠
        for activity in list(activities.values()):
            # 获取活动下所有商品总价格
            total_price = sum((item[0] for item in activity['items']))
            # 获取活动下所有商品总数量
            total_quantity = sum((item[1] for item in activity['items']))
            # 当规则同时具有满足价格 和满足数量的时候 是否叠加处理
            rules = ActivityRule.objects. \
                filter(is_deleted=False,
                       activity__id=activity.id,
                       gift__isnull=False). \
                order_by('accord_cost')
            activity_rule = None
            for rule in rules:
                if total_price < rule:
                    activity_rule = rule
                    break
            # 获取附带赠品
            gift = Sku.objects.get(id=activity_rule.gift)
            # TODO
            # 修改订单信息
        # 状态转变
        order.handle()

    @classmethod
    def set_warehouse_info(cls, order, token=None):
        warehouse_id = order.warehouse_id
        warehouse = get_warehouse_by_id(warehouse_id, token)
        order.warehouse_name = warehouse['warehouse_name']
        order.warehouse_code = warehouse['warehouse_code']
        order.warehouse_province = warehouse['warehouse_province']
        order.warehouse_city = warehouse['warehouse_city']
        order.warehouse_area = warehouse['warehouse_area']
        order.warehouse_detail = warehouse['warehouse_detail']
        order.warehouse_recipient_name = warehouse['warehouse_recipient_name']
        order.warehouse_recipient_contact = \
            warehouse['warehouse_recipient_contact']
        express = cls.get_recommand_express(warehouse['express'])
        order.logistics_name = express['express_name']
        order.logistics_code = express['express_code']
        order.save()
        return order

    @classmethod
    def get_recommand_express(cls, express_list):
        # TODO 可以用随机算法，也可以用价格最低，目前随便返回一个
        return express_list[0]

    @classmethod
    def refund(cls, order):
        logger.debug('enter refund')
        if order.order_status in [50, 60]:
            return {}
        if order.wms_status == 'NEW':
            logger.debug('wms didnot recieve the order')
            inventory_service.InventoryService.clear_locked_inventory(order.id)
            order.order_status = 50
            # 恢复order的标示为正常，不需要人工关闭
            order.order_mark = 10
            order.save()
            return {}
        if order.wms_status in ('ACCEPT', 'EXCEPTION'):
            logger.debug('inform wms to cancel order')
            # 在给仓库发送订单取消的时候，收到应答的时候设置订单的状态了
            OrderCancel(custom_id=order.warehouse_id).delivery_order_cancel(order)
            # 恢复order的标示为正常，不需要人工关闭。
            inventory_service.InventoryService.clear_locked_inventory(order.id)
            order.order_mark = 10
            return {}

        # TODO 退货流程？
        if order.wms_status in ['PARTDELIVERED', 'DELIVERED']:
            # TODO 生成退货单
            order.order_status = 50
            # 恢复order的标示为正常，不需要人工关闭
            order.order_mark = 10
            order.save()

