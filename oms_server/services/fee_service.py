import datetime
import logging
from django.conf import settings
from oms.models.order_express_fee import OrderExpressFee
from oms.models.order_process_fee import OrderProcessFee
from oms.models.storge_fee import StorgeFee
from oms_server.services.inventory_service import InventoryService


"""
费用相关逻辑
"""

logger = logging.getLogger('custom.fee')


class FeeService:

    def create_express_fee(self, order, express, order_express):
        ''' 产生快递费用 '''
        sheet_amount = settings.EXPRESS_SHEET_COST
        amount = self.caculate_express_cost(express, order_express.weight)
        order_express_fee = OrderExpressFee(
            amount=amount,
            sheet_amount=sheet_amount,
            order_id=order.id,
            order_express_id=order_express.id,
            warehouse_id=order.warehouse_id,
            warehouse_name=order.warehouse_name
        )
        order_express_fee.save()
        return order_express_fee

    def create_order_process_fee(self, order, service):
        ''' 订单处理费用 '''
        order_process_fee = OrderProcessFee(
            order_id=order.id,
            order_code=order.order_code,
            amount=int(service['price'] * 100),
            warehouse_id=order.warehouse_id,
            warehouse_name=order.warehouse_name
        )
        order_process_fee.save()
        return order_process_fee

    def create_storge_fee(self, user_id, warehouse_id,
                          warehouse_name, amount, volume):
        storge_fee = StorgeFee(
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name,
            amount=amount,
            volume=volume
        )
        storge_fee.save()
        return storge_fee

    def caculate_express_cost(self, express, weight):
        ''' 计算快递费用 '''
        amount = 0
        if weight <= express['first_weight']:
            amount = int(round(express['first_weight_price'] * 100, 2))
        else:
            amount = express['first_weight_price'] +\
                (weight - express['first_weight']) *\
                express['continued_price']
            amount = int(round(amount * 100, 2))
        return amount

    def caculate_storge_cost(self, warehouse_id, user_id, service):
        '''
        计算仓储费用
        全局扫描，量太大，采用分页 还是 分布式
        '''
        # 获取该用户该仓库下的库存
        inventory = InventoryService().\
            list_all_inventory(user_id=user_id, warehouse_id=warehouse_id)
        print(inventory)
        volume = 0  # 总体积
        for i in inventory:
            volume += self.caculate_volume(i.sku)
        print(type(service['price']), service['price'])
        amount = int(service['price'] * volume * 100)
        return amount, volume
        
    # def caculate_overdue_fee(self, user_id, year, month):
    #     ''' 计算逾期费用, 每月第一天 '''
    #     OrderBill
    #     return year, month

    def caculate_volume(self, sku):
        ''' 计算体积 '''
        try:
            volume = sku.width * sku.length * sku.height
            if not volume:
                volume = 1
                # TODO 需要变更
                # raise Exception()
            return volume
        except Exception as e:
            logger.info("""
                计算sku:{0}体积失败, 长*宽*高:{1}*{2}*{3}
            """.format(sku.id, sku.width,
                       sku.length, sku.height))
