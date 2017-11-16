# -*- coding: utf-8 -*-
# from django.core.paginator import Paginator
from django.db.models import Prefetch
from django.db import transaction
from oms.models.order import Order
from oms.models.order_detail import OrderDetail
from oms.models.sku_warehouse import SkuWarehouse
import logging
logger = logging.getLogger('custom.oms.inventory')


class InventoryService(object):

    @classmethod
    @transaction.atomic
    def lock_inventory(cls, order_id, warehouse_id='0'):
        logger.debug('inventory order : ' + str(order_id))
        order_details = OrderDetail.objects.\
            filter(order_id=order_id, is_deleted=False).\
            select_related('sku')
        is_inventory_enough = True
        for order_detail in order_details:
            logger.debug('inventory order_detail quantity : ' + str(order_detail.quantity))
            if warehouse_id == '0':
                # 返还之前锁定库存
                order_detail.sku.available_quantity += order_detail.locked_total_inventory
                if order_detail.quantity > order_detail.sku.available_quantity:
                    is_inventory_enough = False
                order_detail.sku.available_quantity -= order_detail.quantity
                order_detail.locked_total_inventory = order_detail.quantity
                order_detail.sku.save()
            else:
                sku_warehouse = SkuWarehouse.objects.get(
                    sku=order_detail.sku,
                    warehouse_id=warehouse_id)
                if order_detail.locked_warehouse_inventory != 0:
                    # 如果我们是不是假定两次分配的都是同一个仓库，而且假定路由走到这个流程必然是仓库库存够？？
                    sku_warehouse.available_quantity += order_detail.locked_warehouse_inventory
                if order_detail.quantity > sku_warehouse.available_quantity:
                    is_inventory_enough = False
                sku_warehouse.available_quantity -= order_detail.quantity
                order_detail.locked_warehouse_inventory = order_detail.quantity
                order_detail.locked_warehouse_id = warehouse_id
                sku_warehouse.save()
            order_detail.save()
        if not is_inventory_enough:
            cls.clear_locked_inventory(order_id)
        return {'is_inventory_enough': is_inventory_enough}

    @classmethod
    @transaction.atomic
    def clear_locked_inventory(cls, order_id):
        order_details = OrderDetail.objects.\
            filter(order_id=order_id, is_deleted=False).\
            select_related('sku')
        for order_detail in order_details:
            order_detail.sku.available_quantity += order_detail.locked_total_inventory
            order_detail.locked_total_inventory = 0
            order_detail.sku.save()
            if order_detail.locked_warehouse_inventory != 0:
                sku_warehouse = SkuWarehouse.objects.get(
                    sku=order_detail.sku,
                    warehouse_id=order_detail.locked_warehouse_id)

                sku_warehouse.available_quantity += order_detail.locked_warehouse_inventory
                order_detail.locked_warehouse_inventory = 0
                order_detail.locked_warehouse_id = '0'
                sku_warehouse.save()
            order_detail.save()
        return {}

    @classmethod
    @transaction.atomic
    def delivery_inventory_change(cls, sku, quantity, warehouse_id):
        sku.quantity -= int(quantity)
        sku_warehouse = SkuWarehouse.objects.get(
            sku=sku,
            warehouse_id=warehouse_id)
        sku_warehouse.quantity -= int(quantity)
        sku.save()
        sku_warehouse.save()
        return {}

    # @classmethod
    # def order_lock_all_inventory(cls, sku, quantity):
    #     pass
    #
    # @classmethod
    # def route_lock_warehouse_inventory(cls, warehouse_id, quantity, sku):
    #     pass

    @classmethod
    @transaction.atomic
    def stock_in_inventory_change(cls, sku, quantity, warehouse_id):
        sku.quantity += int(quantity)
        sku.available_quantity += int(quantity)
        sku_warehouse = SkuWarehouse.objects.get(
            sku=sku,
            warehouse_id=warehouse_id)
        sku_warehouse.quantity += int(quantity)
        sku_warehouse.available_quantity += int(quantity)
        sku.save()
        sku_warehouse.save()
        return {}

    @classmethod
    @transaction.atomic
    def stock_out_lock_inventory(cls, sku, quantity, warehouse_id):
        pass

    @classmethod
    @transaction.atomic
    def stock_out_confirm_inventory(cls, sku, quantity, warehouse_id):
        return cls.delivery_inventory_change(sku, quantity, warehouse_id)
