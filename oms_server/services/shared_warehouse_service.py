from django.db.models import Prefetch, Q
from django.core.paginator import Paginator
from oms.models.order import Order
from oms.models.order_detail import OrderDetail
from oms.models.stock_in import StockIn
from oms.models.stock_in_detail import StockInDetail
from oms.models.sku_warehouse import SkuWarehouse
from oms_server.http_service.warehouse_service import list_own_warehouse
from oms.extension.exception import CustomException
''' 共享仓相关逻辑 '''


class SharedWarehouseService:

    def delivery_orders(self, user_id, token,
                        warehouse_id=None, params=None):
        ''' 发货任务 '''
        page_size = int(params.get('page_size', 10))

        warehouses = self.get_shared_warehouse(token)
        warehouse_ids = [w['warehouse_id'] for w in warehouses]
        queryset = None
        order_detail = OrderDetail.objects.\
            filter(is_deleted=False)
        if warehouse_id and warehouse_id in warehouse_ids:
            # TODO 根据抵达时间排序
            queryset = Order.objects.\
                prefetch_related(
                    Prefetch('order_detail',
                             queryset=order_detail,
                             to_attr='order_details')
                ).\
                filter(~Q(wms_status='NEW'), warehouse_id=warehouse_id)
        elif warehouse_id:
            raise CustomException(10013, '仓库不存在')
        else:
            queryset = Order.objects.\
                prefetch_related(
                    Prefetch('order_detail',
                             queryset=order_detail,
                             to_attr='order_details')
                ).\
                filter(~Q(wms_status='NEW'), warehouse_id__in=warehouse_ids)
        if params.get('order_code'):
            # 蘑菇搜索
            queryset = queryset.\
                filter(order_code__contains=params.get('order_code'))
        elif params.get('express_code'):
            pass
        paginator = Paginator(queryset, per_page=page_size)
        return paginator

    def entry_orders(self, user_id, token,
                     params=None, warehouse_id=None):
        ''' 入库任务 '''
        page_size = int(params.get('page_size', 10))

        warehouses = self.get_shared_warehouse(token)
        warehouse_ids = [w['warehouse_id'] for w in warehouses]
        queryset = None
        stock_in_detail = StockInDetail.objects.\
            filter(is_deleted=False)
        if warehouse_id and warehouse_id in warehouse_ids:
            # TODO 根据抵达时间排序
            queryset = StockIn.objects.\
                prefetch_related(
                    Prefetch('stockindetail_set',
                             queryset=stock_in_detail,
                             to_attr='stock_in_details')
                ).\
                filter(~Q(stock_in_status='NEW'), warehouse_id=warehouse_id)
        elif warehouse_id:
            raise CustomException(10013, '仓库不存在')
        else:
            queryset = StockIn.objects.\
                prefetch_related(
                    Prefetch('stockindetail_set',
                             queryset=stock_in_detail,
                             to_attr='stock_in_details')
                ).\
                filter(~Q(stock_in_status='NEW'),
                       warehouse_id__in=warehouse_ids)
        if params.get('stock_in_code'):
            # 蘑菇搜索
            queryset = queryset.\
                filter(stock_in_code__contains=params.get('stock_in_code'))
        elif params.get('express_code'):
            pass
        paginator = Paginator(queryset, per_page=page_size)
        return paginator

    def list_warehouse_inventory(self, user_id, token,
                                 warehouse_id=None, params=None):
        ''' 共享仓用户查看仓库下的库存 '''
        page_size = int(params.get('page_size', 10))
        own_warehouses = list_own_warehouse(token)
        warehouse_ids = [w['warehouse_id'] for w in own_warehouses]
        queryset = None
        if warehouse_id and (warehouse_id in warehouse_ids):
            queryset = SkuWarehouse.objects.\
                select_related('sku').\
                filter(warehouse_id=warehouse_id, is_deleted=False)
        elif warehouse_id:
            raise CustomException(10013, '仓库不存在')
        else:
            queryset = SkuWarehouse.objects.\
                select_related('sku').\
                filter(warehouse_id__in=warehouse_ids, is_deleted=False)
        if params.get('sku_name'):
            print(params.get('sku_name'))
            queryset = queryset.\
                filter(sku__sku_name__contains=params.get('sku_name'))
        elif params.get('item_code'):
            queryset = queryset.\
                filter(sku__item_code__contains=params.get('item_code'))
        elif params.get('bar_code'):
            queryset = queryset.\
                filter(sku__bar_code__contains=params.get('bar_code'))
        paginator = Paginator(queryset, page_size)
        return paginator

    def get_shared_warehouse(self, token):
        ''' 获取共享出去的仓库列表 '''
        warehouses = list_own_warehouse(token)
        return warehouses

    
        