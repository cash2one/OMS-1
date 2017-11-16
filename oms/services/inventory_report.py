# -*- coding: utf-8 -*-
import logging
from oms_server.http_service.warehouse_service import get_warehouse_by_code
from oms.models import inventory_report
from oms.models.inventory_report_item import InventoryReportItem
logger = logging.getLogger('custom.oms.inverntory_report')


class InventoryReport(object):

    @classmethod
    def report(cls, param, data):
        logger.info(param)
        logger.info(data)
        # 根据分页和out_biz_code判重
        # 创建report数据
        # 创建item数据
        # 是否需要库存处理
        # 盘点数据通告货主吗
        # 应答

        app_key = param['app_key']
        warehouse_info = get_warehouse_by_code(
            warehouse_code=data['warehouseCode'],
            wms_app_key=app_key)
        warehouse_id = warehouse_info['warehouse_id']
        # warehouse_id = 'wh100000010003'
        try:
            # TODO  分页的考虑
            report = inventory_report.InventoryReport.objects.get(
                warehouse_id=warehouse_id,
                out_biz_code=data['outBizCode'])
            return {
                'flag': 'success',
                'code': '0',
                'message': ''
            }
        except Exception as e:
            logger.debug(e)
            report = inventory_report.InventoryReport(
                warehouse_code=data['warehouseCode'],
                warehouse_id=warehouse_id,
                # warehouse_name=warehouse_info['warehouse_name'],
                check_order_code=data['checkOrderCode'],
                check_order_id=data.get('checkOrderId', ''),
                owner_code=data['ownerCode'],
                # user_id=data['ownerCode'],
                check_time=data.get('checkTime', ''),
                out_biz_code=data['outBizCode'],
                remark=data.get('warehouseCode', ''),
            )
            report.save()
            if isinstance(data['items']['item'], list):
                items = data['items']['item']
            else:
                items = [data['items']['item']]

            for item in items:
                report_item = InventoryReportItem(
                    inventory_report=report,
                    item_code=item.get('itemCode', ''),
                    item_id=item['itemId'],
                    quantity=item['quantity'],
                )
                report_item.save()

            return {
                'flag': 'success',
                'code': '0',
                'message': ''
            }
