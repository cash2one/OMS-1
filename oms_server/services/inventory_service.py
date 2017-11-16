# -*- coding: UTF-8 -*-
from django.db.models import Prefetch
from django.core.paginator import Paginator
from oms.models.sku import Sku
from oms.models.sku_warehouse import SkuWarehouse
from oms_server.http_service.warehouse_service import get_warehouse_by_id
from oms_server.http_service.warehouse_service import list_own_warehouse
from oms.extension.exception import CustomException


# 库存服务
class InventoryService:

    def list(self, user_id, param=None):
        ''' 用仓用户查看库存 '''
        page_size = param.get('page_size', 10)
        query = Sku.objects.\
            prefetch_related(
                Prefetch('skuwarehouse_set', to_attr='inventories')
            ).\
            filter(user_id=user_id,
                   is_deleted=False)
        if param.get('sku_name'):
            query = query.filter(sku_name__contains=param.get('sku_name'))
        elif param.get('item_code'):
            query = query.filter(item_code__contains=param.get('item_code'))
        elif param.get('bar_code'):
            query = query.filter(bar_code__contains=param.get('bar_code'))
        paginator = Paginator(query, page_size)
        return paginator

    def list_all_inventory(self, user_id, warehouse_id):
        inventory = SkuWarehouse.objects.\
            select_related('sku').\
            filter(user_id=user_id,
                   warehouse_id=warehouse_id)
        return inventory


    # 增加库存
    def create(self, user_id, sku_id, warehouse_id, quantity):
        # 查找对应库存是否存在，
        inventory = None
        try:
            inventory = SkuWarehouse.objects.\
                get(sku_id=sku_id, warehouse_id=warehouse_id, is_deleted=False)
            inventory.quantity = inventory.quantity + quantity
            inventory.available_quantity =\
                inventory.available_quantity + quantity
        except SkuWarehouse.DoesNotExist:
            # 获取仓库信息
            warehouse = get_warehouse_by_id(warehouse_id, user_id)
            inventory = SkuWarehouse(
                sku_id=sku_id,
                warehouse_id=warehouse_id,
                user_id=user_id,
                quantity=quantity,
                available_quantity=quantity,
                warehouse_name=warehouse.name,
                warehosue_province=warehouse.province,
                warehouse_city=warehouse.city,
                warehouse_area=warehouse.area,
                warehouse_detail=warehouse.detail,
                warehouse_longitude=warehouse.longitude,
                warehouse_latitude=warehouse.latitude
            )
        inventory.save()
        return inventory
