# -*- coding: utf-8 -*-
from oms.services.cop_service import Interface


class InvertoryQuery(Interface):

    def __init__(self, method='inventory.query', custom_id='xiaobanma', id=None):
        super().__init__(method=method, custom_id=custom_id, id=id)

    def sync_to_cop(self, warehouse_code, sku_list):
        _obj = {
            'request': {
                'criteriaList': {'criteria': []}
            }
        }
        for sku in sku_list:
            sku_info = {}
            sku_info['warehouseCode'] = warehouse_code
            sku_info['ownerCode'] = sku.user_id
            sku_info['itemCode'] = sku.item_code
            # sku_info['itemId']
            _obj['request']['criteriaList']['criteria'].append(sku_info)

        response = self.process_message(_obj)

        if isinstance(response['items']['item'], list):
            items = response['items']['item']
        else:
            items = [response['items']['item']]

        for item in items:
            pass
