from oms.models.sku import Sku
from oms.models.sku_warehouse import SkuWarehouse


class InventoryService:

    @classmethod
    def sku_get_warehouse(cls, user_id, item_code):
        try:
            sku = Sku.objects.get(user_id=user_id, item_code=item_code)
        except Sku.DoesNotExist:
            return {'is_exist': False}
        list = SkuWarehouse.objects.filter(sku=sku)
        warehouse_list = [{
            'id': ship.warehouse_id,
            'name': ship.warehouse_name,
            'address': ship.warehouse_address,
            'latitude': ship.warehouse_latitude,
            'longitude': ship.warehouse_longitude,
            'total_count': ship.quantity,
            'available_count': ship.available_quantity} for ship in list]
        return {'is_exist': True,
                'total_count': sku.quantity,
                'available_count': sku.available_quantity,
                'sku_id': sku.id,
                'warehouse': warehouse_list
                }

    @classmethod
    def sku_get_warehouse_by_id(cls, sku_id):
        try:
            sku = Sku.objects.get(id=sku_id)
        except Sku.DoesNotExist:
            return {'is_exist': False}
        list = SkuWarehouse.objects.filter(sku=sku)
        warehouse_list = [{
            'id': ship.warehouse.id,
            'name': ship.warehouse_name,
            'address': ship.warehouse_address,
            'total_count': ship.quantity,
            'available_count': ship.available_quantity} for ship in list]
        return {'is_exist': True,
                'total_count': sku.quantity,
                'available_count': sku.available_quantity,
                'sku_id': sku.id,
                'warehouse': warehouse_list
                }
