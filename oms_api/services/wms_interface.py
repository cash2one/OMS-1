# -*- coding: utf-8 -*-
from oms_server.services.stock_in_service import StockInService
from oms.services.delivery_order_service import DeliveryOrderConfirmService
from oms.services.inventory_report import InventoryReport
from oms.services.stockchange_report import StockchangeReport


class WmsInterface(object):

    def __init__(self, param, data):
        self.param = param
        self.data = data

    def entryorder_confirm(self):
        # TODO 暂时不做校验
        return StockInService().confirm(self.param, self.data)

    def deliveryorder_confirm(self):
        return DeliveryOrderConfirmService.confirm(self.param, self.data)

    def inventory_report(self):
        return InventoryReport.report(self.param, self.data)

    def stockchange_report(self):
        return StockchangeReport.report(self.param, self.data)

    # stockout.confirm
    # returnorder.confirm
    # orderprocess.report

    # sn.report
    # wavenum.report
    # deliveryorder.batchcreate.answer
    # deliveryorder.batchconfirm
    # itemlack.report
    # storeprocess.confirm
