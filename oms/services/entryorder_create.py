# -*- coding: utf-8 -*-
from oms.services.cop_service import Interface
from oms.services.singleitem_synchronize import Singleitem
from oms.models.sku import Sku
from oms.models.sku_item_id import SkuItemId
from oms_server.services.balance_service import BalanceService
from oms.extension.exception import CustomException


class EntryOrder(Interface):

    def __init__(self, method='entryorder.create', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def sync_to_cop(self, user_id, stock_in):
        # TODO 余额为负数
        # 在生成发货任务的时候，判断余额，但是在收到WMS发货确认才扣减余额，存在问题
        # if not BalanceService().hava_balance(user_id):
        #     raise CustomException(50004, '账户余额不足，无法生成发货任务')
        # stock_in = self.get(user_id=user_id, stock_in_id=stock_in_id)
        stock_in_obj = {
            'request': {
                'entryOrder': {
                    'entryOrderCode': stock_in.id,
                    'ownerCode': 'aircos',
                    'warehouseCode': stock_in.warehouse_code,
                },
                'orderLines': {'orderLine': []}
            }
        }

        for stock_in_detail in stock_in.stock_in_details:
            # 同步商品
            # TODO 判断该商品是否已同步，或者所有商品已经同步完成
            sku = Sku.objects.get(id=stock_in_detail.sku_id)
            try:
                sku_item_id = SkuItemId.objects.get(
                    sku=sku,
                    warehouse_id=stock_in.warehouse_id)
                item_id = sku_item_id.item_id
            except Exception as e:
                # sku_item_id = Singleitem(custom_id=stock_in.warehouse_id).\
                #     sync_to_cop(
                #         sku=sku,
                #         warehouse_code=stock_in.warehouse_code,
                #         warehouse_id=stock_in.warehouse_id)
                sku_item_id = Singleitem(custom_id=self.custom_id).\
                    sync_to_cop(
                        sku=sku,
                        warehouse_code=stock_in.warehouse_code,
                        warehouse_id=stock_in.warehouse_id)
                if sku_item_id:
                    item_id = sku_item_id.item_id
                else:
                    item_id = None
            order_line = {
                'ownerCode': sku.user_id,
                # 'ownerCode': 'aircos',
                'itemId': item_id,
                'itemCode': sku.item_code,
                'planQty': stock_in_detail.quantity
            }
            # if item_id:
            #     order_line['item_id'] = item_id
            stock_in_obj['request']['orderLines']['orderLine'].append(order_line)

        print(stock_in_obj)
        response = self.process_message(stock_in_obj)

        if 'entryOrderId' in response['response']:
            stock_in.entry_order_id = response['response']['entryOrderId']
        stock_in.stock_in_status = 'ACCEPT'
        stock_in.save()
        return stock_in
