# -*- coding: UTF-8 -*-
from datetime import datetime
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.core.exceptions import ObjectDoesNotExist
from oms.models.stock_in import StockIn
from oms.models.order import Order
from oms.models.sku import Sku
from oms.models.sku_warehouse import SkuWarehouse
from oms.models.stock_in_detail import StockInDetail
# from oms.models.sku_item_id import SkuItemId
from oms.models.stock_in_confirm import StockInConfirm
from oms.extension.exception import CustomException
# from oms.services.cop_service import Interface
from oms.services.id_generation_service import IdGenerationService
from oms.services.entryorder_create import EntryOrder
from oms_server.http_service.warehouse_service import get_warehouse_by_id
from oms_server.http_service.user_service import get_user_info


# 入库单服务
class StockInService:
    # 入库单列表
    def list(self, user_id, param=None):
        page_size = int(param.get('page_size', 10))
        query = StockIn.objects.\
            filter(user_id=user_id,
                   is_deleted=False)
        if 'stockin_code' in param.keys():
            query = query.filter(entry_order_id=param['stockin_code'])
        elif 'express_code' in param.keys():
            query = query.\
                filter(express_number__contains=param['express_code'])
        elif 'sku_name' in param.keys():
            query = query.\
                filter(stockindetail__sku_name=param['sku_name'])
        elif 'item_code' in param.keys():
            query = query.\
                filter(stockindetail__item_code=param['item_code'])
        elif 'user_tel' in param.keys():
            query = query.\
                filter(user_mobile=param['user_tel'])
        elif 'order_code' in param.keys():
            query = query.\
                filter(order_code=param['order_code'])
        elif 'stock_in_type' in param.keys():
            query = query.\
                filter(stock_in_type=int(param['stock_in_type']))
        if param.get('user_name'):
            query = query.filter(user_name=param.get('user_name'))
        if param.get('user_id'):
            query = query.filter(user_id=param.get('user_id'))
        paginator = Paginator(query, page_size)
        return paginator

    def get(self, stock_in_id, user_id):
        stock_in_details = StockInDetail.objects.\
            filter(stock_in_id=stock_in_id, is_deleted=False)
        stock_in = StockIn.objects.\
            prefetch_related(
                Prefetch('stockindetail_set', queryset=stock_in_details,
                         to_attr='stock_in_details')
            ).\
            get(id=stock_in_id, user_id=user_id,
                is_deleted=False)
        return stock_in

    # 在创建入库单的时候就会同步到COP
    # 如果同步失败，则会一直重试
    # 只有推送成功，才会存储到数据库
    @transaction.atomic
    def create(self, user_id, token, data, user_name=None):
        s = ';'
        user_info = get_user_info(user_id)
        express_number = s.join(data.get('express_number', []))
        stock_in = StockIn(
            stock_in_type=int(data.get('stock_in_type', 1)),
            warehouse_id=data['warehouse_id'],
            express=data.get('express'),
            express_number=express_number,
            warehouse_code=data.get('warehouse_code'),
            warehouse_name=data.get('warehouse_name'),
            wms_app_key=data.get('wms_app_key'),
            user_note=data.get('user_note'),
            estimated_to_arrival=datetime.fromtimestamp(int(data.get('estimated_to_arrival'))),
            user_id=user_id,
            user_name=user_name,
            user_mobile=user_info['phone'],
            id=IdGenerationService.generate_stock_in_id()
        )
        # 获取仓库信息，修改入库单的发货和收货信息
        # 可能存在不能获取到信息的情况
        warehouse = get_warehouse_by_id(data['warehouse_id'], token)
        stock_in.sender_phone = data.get('sender_phone', '')
        stock_in.send_name = data.get('sender_name', '')
        stock_in.recipient_phone = warehouse['warehouse_recipient_contact']
        stock_in.recipient_name = warehouse['warehouse_recipient_name']
        # 如果是退货入库，必须关联退货订单
        if int(data['stock_in_type']) == 2:
            try:
                order = Order.objects.get(id=data['order_id'])
                stock_in.order_code = order.order_code
            except AttributeError:
                raise CustomException('10003', 'order_id not exist')
            except ObjectDoesNotExist:
                raise CustomException('10009')
        if not data.get('skues'):
            raise CustomException('10020', '请填写商品信息')
        create_stock_in_details = []
        for sku_info in data['skues']:
            sku = Sku.objects.get(id=sku_info['sku_id'])
            stock_in_detail = StockInDetail(
                quantity=sku_info['quantity'],
                sku_id=sku_info['sku_id'],
                stock_in_id=stock_in.id,
                sku_name=sku.sku_name,
                sku_spec=sku.specification,
                bar_code=sku.bar_code,
                item_code=sku.item_code,
                user_id=user_id
            )
            create_stock_in_details.append(stock_in_detail)
        stock_in.save()
        StockInDetail.objects.bulk_create(create_stock_in_details)
        stock_in.stock_in_details = create_stock_in_details
        # data['warehouse_id']
        # EntryOrder(custom_id='xiaobanma').\
        #     sync_to_cop(user_id, stock_in)
        EntryOrder(custom_id=data['warehouse_id']).\
            sync_to_cop(user_id, stock_in)
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

    def update(self, stock_in_id, user_id, data):
        stock_in = StockIn.objects.\
            get(id=stock_in_id, is_deleted=False, user_id=user_id)
        update_fields = ['express', 'express_number', 'order_code',
                         'user_note', 'estimated_to_arrival', 'stock_in_type']
        for key in data.keys():
            if key in update_fields:
                setattr(stock_in, key, update_fields)
        if data.get('stock_in_type', stock_in.stock_in_type) != stock_in.stock_in_type:
            if 'order_code' in data.keys() and data['stock_in_type'] == 2:
                stock_in.order_code = data['order_code']
            else:
                stock_in.order_code = None
        else:
            if 'order_code' in data.keys() and stock_in.stock_in_type == 2:
                stock_in.order_code = data['order_code']

        # 更新商品信息

        stock_in.save()
        return stock_in

    def delete(self, stock_in_id, user_id):
        stock_in = StockIn.objects.\
            get(user_id=user_id, id=stock_in_id)
        stock_in.is_deleted = True
        stock_in.save()
        return stock_in

    @transaction.atomic
    def confirm(self, params, data):
        try:
            # if 'entryOrderId' in data['entryOrder']:
            #     stock_in = StockIn.objects.get(
            #         entry_order_id=data['entryOrder']['entryOrderId'],
            #         wms_app_key=params['app_key'],
            #         warehouse_code=data['entryOrder']['warehouseCode']
            #     )
            # else:
            #     stock_in = StockIn.objects.get(
            #         entry_order_code=data['entryOrder']['entryOrderCode']
            #     )
            stock_in = StockIn.objects.get(
                id=data['entryOrder']['entryOrderCode'])
            warehouse = get_warehouse_by_id(stock_in.warehouse_id)
            # TODO 收到重复的outBizCode应该怎么处理
            # if stock_in.out_biz_code == data['entryOrder']['outBizCode']:
            #     return {
            #         'flag': 'success',
            #         'code': '0',
            #         'message': ''
            #     }
            if StockInConfirm.objects.filter(out_biz_code=data['entryOrder']['outBizCode']):
                return {
                    'flag': 'success',
                    'code': '0',
                    'message': ''
                }
            stock_in.stock_in_status = data['entryOrder']['status']
            # stock_in.out_biz_code = data['entryOrder']['outBizCode']
            stock_in.save()

        except Exception as e:
            print(e)
            return {
                'flag': 'failure',
                'code': '10010',
                'message': 'no this entryorder info'
            }
        # TODO  多行处理
        # for order_line in data['orderLines']:
        if isinstance(data['orderLines']['orderLine'], list):
            order_lines = data['orderLines']['orderLine']
        else:
            order_lines = [data['orderLines']['orderLine']]

        for order_line in order_lines:
            # TODO   need to store in db(new table?) to trace and show?
            try:
                # if 'itemId' in order_line:
                #     stock_in_detail = StockInDetail.objects.get(
                #         stock_in=stock_in,
                #         item_id=order_line['itemId']
                #     )
                # else:
                #     stock_in_detail = StockInDetail.objects.get(
                #         stock_in=stock_in,
                #         item_code=order_line['itemCode']
                #     )
                stock_in_detail = StockInDetail.objects.get(
                    stock_in=stock_in,
                    item_code=order_line['itemCode']
                )
                stock_in_detail.sku.quantity += int(order_line['actualQty'])
                stock_in_detail.sku.available_quantity += int(order_line['actualQty'])
                stock_in_detail.sku.save()
            except Exception as e:
                print(e)
                return {
                    'flag': 'failure',
                    'code': '10011',
                    'message': 'no this sku info'}
            try:
                sku_warehouse = SkuWarehouse.objects.get(
                    sku=stock_in_detail.sku,
                    warehouse_id=stock_in.warehouse_id
                )
                sku_warehouse.quantity += int(order_line['actualQty'])
                sku_warehouse.available_quantity += int(order_line['actualQty'])
                sku_warehouse.save()
            except Exception as e:
                print(e)
                sku_warehouse = SkuWarehouse(
                    sku=stock_in_detail.sku,
                    warehouse_id=stock_in.warehouse_id,
                    quantity=int(order_line['actualQty']),
                    available_quantity=int(order_line['actualQty']),
                    user_id=stock_in.user_id,
                    warehouse_name=warehouse['warehouse_name'],
                    warehouse_province=warehouse['warehouse_province'],
                    warehouse_city=warehouse['warehouse_city'],
                    warehouse_area=warehouse['warehouse_area'],
                    warehouse_detail=warehouse['warehouse_detail'],
                    warehouse_longitude=warehouse['warehouse_longitude'],
                    warehouse_latitude=warehouse['warehouse_latitude']
                )
                sku_warehouse.save()

            stock_in_confirm = StockInConfirm(
                plan_quantity=order_line['planQty'],
                actual_quantity=order_line['actualQty'],
                inventory_type=order_line.get('inventoryType', 'ZP'),
                # sku_name=models.CharField(max_length=128, verbose_name='商品名称'),
                # sku_spec=models.CharField(max_length=128, verbose_name='商品规格'),
                item_code=order_line['itemCode'],
                item_id=order_line.get('itemId', ''),
                out_biz_code=data['entryOrder']['outBizCode'],
                # bar_code=,
                sku=stock_in_detail.sku,
                user_id=stock_in_detail.sku.user_id,
                stock_in=stock_in,
            )
            stock_in_confirm.save()

        return {
            'flag': 'success',
            'code': '0',
            'message': ''
        }

    def cancle(self,user_id,stock_in_id):

        # 通过 stock_in_details 得到 stock_in 得到入库单
        # stock_in_details = StockInDetail.objects.\
        #     filter(stock_in_id=stock_in_id, is_deleted=False)
        # stock_in = StockIn.objects.\
        #     prefetch_related(
        #         Prefetch('stockindetail_set', queryset=stock_in_details,
        #                  to_attr='stock_in_details')
        #     ).\
        #     get(id=stock_in_id, user_id=user_id,
        #         is_deleted=False)

        # 直接 获取 stock_in
        # why details?
        stock_in = StockIn.objects. \
            get(user_id=user_id, id=stock_in_id)

        # TODO cop>wms 交互
        stock_in.stock_in_status = 'CANCELED'

        return stock_in





