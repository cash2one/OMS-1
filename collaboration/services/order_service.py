# -*- coding: UTF-8 -*-
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.db.models.fields.related import ForeignKey
from django.db import transaction
from oms.models.order import Order
from oms.models.order_express import OrderExpress
from oms.models.sku_warehouse import SkuWarehouse
from oms.models.order_detail import OrderDetail
from oms.models.split_combine_order import SplitCombineOrder
from oms.extension.exception import CustomException
from itertools import combinations
from oms_server.extension import map_utils
from oms.extension.logger import time_logger
from oms_server.http_service.warehouse_service import get_warehouse_by_id
from oms.services.id_generation_service import IdGenerationService
from oms.services.inventory_service import InventoryService
from oms.services.deliveryorder_create import DeliveryOrder


class OrderService:

    # 支持条件查询
    @time_logger
    def list(self, kwargs):
        is_unhandle = True if kwargs.get('is_unhandle') == 'true' else False
        page_size = kwargs.get('page_size', 10)
        order_express = OrderExpress.objects.filter(is_deleted=False)
        query = Order.objects.\
            prefetch_related(
                Prefetch('orderexpress_set', order_express, to_attr='order_express')
            ).\
            select_related('store')
        if kwargs.get('order_code'):
            query = query.filter(order_code=kwargs.get('order_code'))
        elif kwargs.get('sku_name'):
            query = query.filter(order_detail__sku__sku_name=kwargs.get('sku_name'))
        elif kwargs.get('item_code'):
            query = query.filter(order_detail__sku__item_code=kwargs.get('item_code'))
        elif kwargs.get('consignee_name'):
            query = query.filter(consignee_name=kwargs.get('consignee_name'))
        elif kwargs.get('exress_number'):
            query = query.filter(express_number=kwargs.get('express_number'))
        if kwargs.get('pay_time_start') and kwargs.get('pay_time_end'):
            pay_date_start = datetime.\
                fromtimestamp(int(kwargs.get('pay_time_start')))
            pay_date_end = datetime.\
                fromtimestamp(int(kwargs.get('pay_time_end')))
            query = query.filter(pay_time__range=[pay_date_start, pay_date_end])
        if kwargs.get('store_name'):
            query = query.filter(store__store_name=kwargs.get('store_name'))
        if kwargs.get('buyer_nickname'):
            query = query.filter(buyer_nickname=kwargs.get('buyer_nickname'))
        if kwargs.get('buyer_note'):
            query = query.filter(buyer_note=kwargs.get('buyer_note'))
        if kwargs.get('order_mark'):
            print(kwargs.get('order_mark'))
            query = query.filter(order_mark=int(kwargs.get('order_mark')))
        if kwargs.get('order_status'):
            print(kwargs.get('order_status'))
            query = query.filter(order_status=int(kwargs.get('order_status')))
        if kwargs.get('is_locked') is not None:
            is_locked = True if kwargs.get('is_locked') == 'true' else False
            query = query.filter(is_locked=is_locked)
        if kwargs.get('consignee_province'):
            query = query.\
                filter(consignee_province=kwargs.get('consignee_province'))
        if kwargs.get('consignee_city'):
            query = query.filter(consignee_city=kwargs.get('consignee_city'))
        if kwargs.get('consignee_area'):
            query = query.filter(consignee_area=kwargs.get('consignee_area'))
        if kwargs.get('consignee_phone'):
            query = query.filter(consignee_phone=kwargs.get('consignee_phone'))
        if kwargs.get('user_name'):
            query = query.filter(user_name=kwargs.get('user_name'))
        if kwargs.get('user_id'):
            query = query.filter(user_id=kwargs.get('user_id'))
        if is_unhandle:
            query = query.filter(Q(order_status=10) | Q(is_locked=True))
        paginator = Paginator(query, page_size)
        return paginator

    def order_check(self, order_id):

        # 获取订单
        order = self.get(order_id=order_id)
        if order.order_status != 10 or order.order_mark == 40:
            raise CustomException('10011', '该订单无法审核')
        validation_errors = []

        # 校验　地址
        address = order.consignee_province + order.consignee_city +\
            order.consignee_area + order.consignee_detail
        if not self.validate_address(address):
            validation_errors.append('invalid address')

        # 获取　订单sku id:数量
        sku_infoes = {}
        for order_detail in order.order_details:
            if order_detail.sku_id not in sku_infoes:
                sku_infoes[order_detail.sku_id] = order_detail.quantity
            else:
                sku_infoes[order_detail.sku_id] += order_detail.quantity
        # 校验　库存
        for sku_info_id, sku_info_quantity in sku_infoes.items():
            inventories = self.\
                get_inventory(sku_id=sku_info_id,
                              warehouse_id=order.warehouse_id)
            inventory = sum([i.available_quantity for i in inventories])
            if inventory < sku_info_quantity:
                validation_errors.\
                    append('sku: %s inventory shortage' % sku_info_id)

        # 若没有校验错误，则更改订单状态，否则抛出异常
        if not validation_errors:
            print('审核通过')
            order.order_status = 20  # 审核通过
            order.order_status_info = '已审核'
            order.order_mark = 10  # 正常订单
            order.operate_time = datetime.now()
            # 锁定库存
            InventoryService.lock_inventory(order_id=order_id)
            order.save()
        else:
            raise CustomException(error_code='10010',
                                  error_message=validation_errors)
        return order

    def validate_address(self, raw_address):
        keys_zh = r'[^\u4e00-\u9fa5^A-Za-z_0-9,\,\:\.\x00,\，\：\ \。\#]'
        if (raw_address == ""):
            return False
        return True

    def get(self, order_id):
        order_details = OrderDetail.objects.\
            filter(order_id=order_id, is_deleted=False).\
            select_related('sku')
        order = Order.objects.\
            prefetch_related(
                Prefetch('order_detail', queryset=order_details,
                         to_attr='order_details')
            ).\
            select_related('store').\
            get(id=order_id)
        return order

    # 编辑订单
    @transaction.atomic
    def update(self, order_id, data):
        self.update_base_info(order_id=order_id, data=data)
        if 'order_details' in data.keys():
            self.update_sku_info(order_id=order_id,
                                 data=data)
        return self.get(order_id=order_id)

    # 路由订单
    # TODO 使用numpy,构建多维矩阵
    def route_order(self, order_id):
        self.order = self.get(order_id=order_id)

        # 获取订单里的sku的库存分布
        # 指定了发货仓库或者没有指定仓库
        # 获取订单需要的sku 数量
        self.sku_required_quantity = {}
        for order_detail in self.order.order_details:
            if order_detail.sku_id not in self.sku_required_quantity:
                self.sku_required_quantity[order_detail.sku_id] =\
                    order_detail.quantity
            else:
                self.sku_required_quantity[order_detail.sku_id] +=\
                    order_detail.quantity

        # 库存分布情况
        self.inventory_distribution = {}
        self.warehouses = {}
        for sku_id, sku_quantity in self.sku_required_quantity.items():
            inventories = self.\
                get_inventory(sku_id, warehouse_id=self.order.warehouse_id)
            print(inventories)
            for inventory in inventories:
                # 设置库存分布
                self.inventory_distribution.\
                    setdefault(inventory.warehouse_id, [])
                self.inventory_distribution[inventory.warehouse_id].\
                    append(inventory)
                # 获取仓库信息
                if inventory.warehouse_id not in self.warehouses:
                    # 好像有Bug!!!
                    self.warehouses[inventory.warehouse_id] =\
                        self.get_warehouse(inventory.warehouse_id)
        # 可选仓库组合和一个组合因子
        # 1：不拆单
        # 2：拆两单
        # ......
        available_combination = self.\
            recure_combinations(self.inventory_distribution.keys(), 1)
        # 根据挑选出来的最优仓库组合拆单
        split_orders = self.split_order(order=self.order,
                                        combination=available_combination)
        print("=====================matrix=======================")
        print("\n\n")
        print("required_quantity:", self.sku_required_quantity)
        print("inventory_distribution:", self.inventory_distribution)
        print("available_combination", available_combination)
        print("split orders:", split_orders)
        print("=======================matrix=========================")
        return split_orders

    # 获取仓库信息,并设置距离权重
    def get_warehouse(self, warehouse_id):
        # TODO 获取仓库信息
        warehouse = get_warehouse_by_id(warehouse_id=warehouse_id)
        destination = self.order.consignee_province +\
            self.order.consignee_city + self.order.consignee_area +\
            self.order.consignee_detail
        source = warehouse['warehouse_province'] + warehouse['warehouse_city'] +\
            warehouse['warehouse_area'] + warehouse['warehouse_detail']
        distance = map_utils.get_distance(source, destination)
        warehouse['distance'] = distance
        return warehouse

    # 递归组合，返回最小拆单数的所有组合
    def recure_combinations(self, keys, n):
        result_list = []
        # 控制递归深度
        if n > len(keys):  # 可以减少次数
            return None
        for item in combinations(keys, n):
            # 校验组合是否合法
            result = self.check_combinations_invalid(item, n)
            if result:
                result_list.append(result)
        if not result_list:
            return self.recure_combinations(keys, n+1)
        else:
            sorted_result = sorted(result_list,
                                   key=lambda x: x[1])
            return sorted_result[0][0]

    # 拆单
    def split_order(self, order, combination):
        create_orders = []
        if not combination:
            raise CustomException("库存不足，无法发货")
        if len(combination) == 1:
            order.warehouse_id = [key for key in combination.keys()][0]
            warehouse = self.warehouses.get(order.warehouse_id)
            order.is_splited = False
            # 指定仓库地址 为 发货地址
            self.set_warehouse(order, warehouse)
            # 锁定仓库的可用库存
            InventoryService.lock_inventory(order.id, order.warehouse_id)
            express = self.get_recommand_express(warehouse['express'])
            order.logistics_name = express['express_name']
            order.logistics_code = express['express_code']
            order.save()
            DeliveryOrder(custom_id='xiaobanma', id=order.id).sync_to_cop(order)
            create_orders.append(order)
        else:
            # 需要拆单
            order.is_splited = True
            order.save()
            # 先把锁定的库存换会去
            InventoryService.clear_locked_inventory(order.id)
            create_order_details = []
            for warehouse, skues in combination.items():
                # 一次循环，拆成一笔订单
                _order = self.copy_order(order)
                _order.warehouse_id = warehouse
                self.set_warehouse(_order, self.warehouses.get(warehouse))
                express = self.get_recommand_express(warehouse['express'])
                _order.logistics_name = express['express_name']
                _order.logistics_code = express['express_code']
                _order.save()
                create_orders.append(_order)
                # 获取仓库里的sku 数量，创建order_detail
                for sku in skues:
                    for order_detail in order.order_details:
                        if order_detail.sku_id == sku[0]:
                            _order_detail = OrderDetail(
                                sku_id=sku[0],
                                quantity=sku[1],
                                order_id=_order.id
                            )
                            _order_detail.save()
                            create_order_details.append(_order_detail)
                # 先锁定总库存
                InventoryService.lock_inventory(_order.id)
                # 然后锁定仓库的库存
                InventoryService.lock_inventory(_order.id, _order.warehouse_id)

            # OrderDetail.objects.bulk_create(create_order_details)
            # 保存子订单和主订单之间的关系
            for idx, sub_order in enumerate(create_orders):
                split_order = SplitCombineOrder(
                    sub_order_sequence=idx,
                    new_order=sub_order.id,
                    original_order=order.id,
                    is_splited=True)
                split_order.save()
        return create_orders

    def get_recommand_express(self, express_list):
        # TODO 可以用随机算法，也可以用价格最低，目前随便返回一个
        return express_list[0]

    # 复制订单主要信息
    def copy_order(self, order):
        _order = Order()
        for f in order._meta.fields:
            if isinstance(f, ForeignKey):
                setattr(_order, '%s_id', getattr(order, '%s_id' % f.name))
            else:
                setattr(_order, f.name, getattr(order, f.name))
        order_id = IdGenerationService.generate_order_id()
        _order.id = order_id
        _order.order_details = []
        return _order

    # 设置仓库信息
    def set_warehouse(self, order, warehouse):
        order.warehouse_name = warehouse['warehouse_name']
        order.warehouse_code = warehouse['warehouse_code']
        order.warehouse_province = warehouse['warehouse_province']
        order.warehouse_city = warehouse['warehouse_city']
        order.warehouse_area = warehouse['warehouse_area']
        order.warehouse_detail = warehouse['warehouse_detail']
        order.warehouse_recipient_name = \
            warehouse['warehouse_recipient_name']
        order.warehouse_recipient_contact = \
            warehouse['warehouse_recipient_contact']

        return order

    # 检查组合的合法性
    # 返回值：
    # 组合仓库，每个仓库发的sku情况
    def check_combinations_invalid(self, combination, n):
        # 成功标志
        tag = True
        # 返回结果
        result = {}
        # 计算给个sku，能否在该组合中获取到，有一个不行，则非法
        for sku_id in self.sku_required_quantity.keys():
            a = 0
            # sku在各个仓库中的分布情况
            sku_quantity_list = []
            for i in range(n):
                # 获取组合中，每个sku能拿到的数量
                available_quantities = [
                    value.available_quantity
                    for value in self.inventory_distribution[combination[i]]
                    if value.sku_id == sku_id]
                available_quantities = available_quantities[0]\
                    if available_quantities else 0
                a = a + available_quantities
                sku_quantity_list.\
                    append((combination[i], available_quantities))
                # TODO 怎么获取sku选择数量
            # 如果在组合中，拿到的sku总数大于需要的sku数量
            # 那么这个组合，能满足该sku
            required_quantity = self.sku_required_quantity[sku_id]
            if required_quantity <= a:
                _sorted = sorted(sku_quantity_list,
                                 key=lambda x: x[1])
                # 应该不会出负数．．
                while required_quantity:
                    item = _sorted.pop(-1)
                    result.setdefault(item[0], {})
                    result[item[0]][sku_id] =\
                        item[1] if item[1] <= required_quantity else required_quantity
                    required_quantity = required_quantity -\
                        (item[1]
                         if item[1] <= required_quantity
                         else required_quantity)
            else:
                tag = False
                break
        if tag:
            # 计算返回的组合的距离权值
            total_distance = 0
            for key in result.keys():
                total_distance += self.warehouses.get(key)['distance']
            return result, total_distance

    # 更新order基本信息
    def update_base_info(self, user_id, order_id, data):
        order = Order.objects.get(user_id=user_id, id=order_id)
        update_fileds = [
            'consignee_name', 'consignee_phone', 'consignee_province',
            'consignee_province', 'consignee_city', 'consignee_area',
            'consignee_detail', 'buyer_note', 'user_note', 'express',
            'warehouse_id', 'warehouse_name', 'warehouse_code'
        ]
        for i in data.keys():
            if i in update_fileds:
                setattr(order, i, data[i])
        order.save()
        return order

    def _get(self, order_id):
        order_details = OrderDetail.objects.\
            filter(order_id=order_id, is_deleted=False).\
            select_related('sku')
        order = Order.objects.\
            prefetch_related(
                Prefetch('order_detail', queryset=order_details,
                         to_attr='order_details')
            ).\
            select_related('store').\
            get(id=order_id)
        return order

    # 锁定订单
    def lock_order(self, order_id, lock_reanson):
        order = Order.objects.get(id=order_id)
        order.is_locked = True
        order.mark_reason = lock_reanson
        # 订单标记：锁定
        order.order_mark = 40
        order.save()
        return order

    # 订单解锁
    def unlock_order(self, order_id):
        order = Order.objects.get(id=order_id)
        order.is_locked = False
        # 订单标记：待人工审核
        order.order_mark = 20
        order.save()
        return order

    # 更新
    # @transaction.atomicorder_detail
    def update_order_detail_info(self, data):
        order_detail = OrderDetail.objects.\
            get(id=data['order_detail_id'])
        update_fileds = [
            'quantity', 'price'
        ]
        for i in data.keys():
            if i in update_fileds:
                setattr(order_detail, i, data[i])
        order_detail.save()
        return order_detail

    # 编辑商品信息
    def update_sku_info(self, order_id, data):
        create_order_details = []
        for order_detail_data in data['order_details']:
            order_detail = OrderDetail(
                is_gift=False,
                quantity=order_detail_data['quantity'],
                total_price=order_detail_data['price'],
                sku_id=order_detail_data['sku_id'],
                order_id=order_id
            )
            create_order_details.append(order_detail)
        # 删除之前所有关联的订单详情
        OrderDetail.objects.\
            filter(order_id=order_id).\
            filter(is_deleted=False).\
            update(is_deleted=True)
        for i in create_order_details:
            print(i.sku_id)
        OrderDetail.objects.bulk_create(create_order_details)

    # 获取sku库存
    def get_inventory(self, sku_id, warehouse_id):
        inventories = None
        if not warehouse_id:
            inventories = SkuWarehouse.objects.\
                filter(sku_id=sku_id)
            print(inventories)
        else:
            inventories = SkuWarehouse.objects.\
                filter(sku_id=sku_id, warehouse_id=warehouse_id)
            print(inventories)
        return inventories

    def get_sku_infoes(self, order_id):
        order_details = OrderDetail.objects.\
            select_related('sku')
        return order_details
