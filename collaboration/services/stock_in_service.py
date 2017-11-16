# -*- coding: UTF-8 -*-
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
from oms.models.stock_in import StockIn
from oms.models.sku_warehouse import SkuWarehouse
from oms.models.stock_in_detail import StockInDetail
from oms.services.entryorder_create import EntryOrder


# 入库单服务
class StockInService:
    # 入库单列表
    def list(self, param=None):
        page_size = int(param.get('page_size', 10))
        query = StockIn.objects.\
            filter(is_deleted=False)
        if 'stock_in_code' in param.keys():
            query = query.filter(stock_in_code=param['stock_in_code'])
        elif 'express_number' in param.keys():
            query = query.\
                filter(express_number__contains=param['express_number'])
        elif 'sku_name' in param.keys():
            query = query.\
                filter(stockindetail__sku_name=param['sku_name'])
        elif 'item_code' in param.keys():
            query = query.\
                filter(stockindetail__item_code=param['item_code'])
        elif 'user_mobile' in param.keys():
            query = query.\
                filter(user_mobile=param['user_mobile'])
        elif 'order_code' in param.keys():
            query = query.\
                filter(order_code=param['order_code'])
        elif 'stock_in_type' in param.keys():
            query = query.\
                filter(stock_in_type=int(param['stock_in_type']))
        elif param.get('user_name'):
            query = query.filter(user_name=param.get('user_name'))
        elif param.get('user_id'):
            query = query.filter(user_id=param.get('user_id'))
        paginator = Paginator(query, page_size)
        return paginator

    def get(self, stock_in_id):
        stock_in_details = StockInDetail.objects.\
            filter(stock_in_id=stock_in_id, is_deleted=False)
        stock_in = StockIn.objects.\
            prefetch_related(
                Prefetch('stockindetail_set', queryset=stock_in_details,
                         to_attr='stock_in_details')
            ).\
            get(id=stock_in_id,
                is_deleted=False)
        return stock_in

    # 更新库存
    # 原子更新
    @transaction.atomic
    def update_inventory(self, stock_in):
        for stock_in_detail in stock_in.stock_in_details:
            try:
                inventory = SkuWarehouse.\
                    objects.\
                    get(sku_id=stock_in_detail.sku_id,
                        warehouse_id=stock_in.warehouse_id)
                # 若是之前已经，有对应的库存信息，那么增加数量
                inventory.quantity += stock_in_detail.quantity
                inventory.available_quantity += stock_in_detail.quantity
                inventory.save()
            except ObjectDoesNotExist as e:
                # 若是不存在，那么创建相应的库存
                inventory = SkuWarehouse(
                    quantity=stock_in_detail.quantity,
                    available_quantity=stock_in_detail.quantity,
                    sku_id=stock_in.sku_id,
                    warehouse_id=stock_in.warehouse_id,
                    user_id=stock_in.user_id
                )
                inventory.save()
        return None

    def update(self, stock_in_id, data):
        stock_in = StockIn.objects.\
            get(id=stock_in_id, is_deleted=False)
        # update_fields = ['express', 'express_number', 'order_code',
        #                  'user_note', 'estimated_to_arrival', 'stock_in_type']
        # for key in data.keys():
        #     if key in update_fields:
        #         setattr(stock_in, key, update_fields)
        # if data.get('stock_in_type', stock_in.stock_in_type) != stock_in.stock_in_type:
        #     if 'order_code' in data.keys() and data['stock_in_type'] == 2:
        #         stock_in.order_code = data['order_code']
        #     else:
        #         stock_in.order_code = None
        # else:
        #     if 'order_code' in data.keys() and stock_in.stock_in_type == 2:
        #         stock_in.order_code = data['order_code']

        # # 更新商品信息

        # stock_in.save()
        # EntryOrder(custom_id='xiaobanma').\
        #     sync_to_cop(stock_in.user_id, stock_in)
        return stock_in

    def delete(self, stock_in_id, user_id):
        stock_in = StockIn.objects.\
            get(user_id=user_id, id=stock_in_id)
        stock_in.is_deleted = True
        stock_in.save()
        return stock_in
