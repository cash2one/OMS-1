# -*- coding: utf-8 -*-
import logging
from oms_server.http_service.warehouse_service import get_warehouse_by_code
from oms.models import stockchange_report

logger = logging.getLogger('custom.oms.inverntory_report')


class StockchangeReport(object):

    @classmethod
    def report(cls, param, data):
        logger.debug(param)
        logger.debug(data)
        # 确定仓库
        # out_biz_code判重
        # 创建item数据
        # 是否需要库存处理
        # 盘点异动数据通告货主吗
        # 应答
        if isinstance(data['items']['item'], list):
            items = data['items']['item']
        else:
            items = [data['items']['item']]

        app_key = param['app_key']
        warehouse_info = get_warehouse_by_code(
            warehouse_code=items[0]['warehouseCode'],
            wms_app_key=app_key)
        warehouse_id = warehouse_info['warehouse_id']

        # warehouse_id = 'wh100000010003'

        for item in items:
            try:
                stockchange_report.StockchangeReport.objects.get(
                    warehouse_id=warehouse_id,
                    out_biz_code=item['outBizCode'])
                continue
            except Exception as e:
                logger.debug(e)
                st_report = stockchange_report.StockchangeReport(
                    warehouse_id=warehouse_id,
                    owner_code=item['ownerCode'],
                    warehouse_code=item['warehouseCode'],
                    order_code=item['orderCode'],
                    out_biz_code=item['outBizCode'],
                    item_code=item['itemCode'],
                    quantity=item['quantity'],
                )
                st_report.save()
        return {
            'flag': 'success',
            'code': '0',
            'message': ''
        }
