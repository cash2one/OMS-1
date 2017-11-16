# -*- coding: utf-8 -*-
from oms.services.cop_service import Interface
from oms.models.sku_item_id import SkuItemId


class Singleitem(Interface):
    def __init__(self, method='singleitem.synchronize', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def sync_to_cop(self, sku, warehouse_code, warehouse_id):
        _obj = {
            'request': {
                'acitionType': 'add',
                'warehouseCode': warehouse_code,
                'ownerCode': sku.user_id,
                # 'ownerCode': 'aircos',
                'item': {
                    'itemCode': sku.item_code,
                    'itemName': sku.sku_name,
                    'barCode': sku.bar_code,
                    'itemType': sku.item_type
                }
            }
        }
        response = self.process_message(_obj)
        item_id = response['response']['itemId']
        if item_id:
            sku_item_id = SkuItemId(
                sku=sku,
                warehouse_id=warehouse_id,
                item_id=item_id,
                item_code=sku.item_code,
                user_id=sku.user_id
            )
            sku_item_id.save()
            return sku_item_id
        else:
            return None
