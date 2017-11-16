# coding:utf-8
import json
import time
import xmltodict
import requests
import logging
from oms.models.order import Order
from oms.models.stock_in import StockIn
from oms_server.custom_celery import app
from oms.models.sku import Sku
from oms.models.store import Store
from oms_server.services.platforms import common_params
from oms_server.services.platforms import interface
from oms.extension.exception import CustomException
from oms.services.id_generation_service import IdGenerationService
from oms_server.services.billing_service import BillingService
from oms_server.services.token_service import TokenService
from oms.settings import test

logger = logging.getLogger('custom.task')


@app.task
def storge_billing():
    result = BillingService().storge_billing()
    print(result)
    return result


@app.task
def overdue_billing():
    result = BillingService().overdue_billing()
    print(result)
    return 'success'


# user_param：用户传入参数，回调是原样返回；status:1 开始；2：结束
def ware_detail_callback(
        user_param,
        store_detail,
        sku_item,
        wares_total,
        sku_total,
        status):
    if status["callback_status"] == "end":
        start_stamp = status["start_stamp"]
        end_stamp = status["end_stamp"]
        msg = str.format(
            "%s[%s]商品同步已完成，%s个商品%s个SKU，共耗时%s秒" %
            (store_detail["platform_name"], store_detail["store_name"],
             wares_total, sku_total, round(end_stamp - start_stamp, 1)))
        # print(msg)
        logging.info(msg)
        headers = {'token': user_param["token"]}
        data = {
            "msg_type": 3,
            "msg_title": "商品同步完成通知",
            "msg_body": msg
        }
        try:
            url = str.format(
                "%s/api/messages/put" % test.CMM_URL)
            resp = requests.post(url=url, headers=headers, data=data)
            res = json.loads(resp.text)
            if "error_code" not in res and res["error_code"] != 0:
                logging.warning("商品同步时发送消息返回失败，url:%s; return:%s" % (url, res))
        except BaseException as e:
            logging.warning("商品同步时发送消息失败，error:%s" % (str(e)))
        return True
    else:
        sku = Sku(**sku_item)
        sku_old = Sku.objects.filter(
            item_code=sku_item['item_code'],
            user_id=sku_item['user_id'])
        if sku_old:
            sku_old.update(**sku_item)
        else:
            sku.id = IdGenerationService.generate_sku_id(
                store_detail["user_id"])
            sku.save()
        # print(
        #     "SKU编码 = %s, SKU名称 = %s SKU价格 = %s" %
        #     (sku_item["item_code"], sku_item["sku_name"], sku_item["price"]))


@app.task
def sync_products(store_detail, token):
    ''' 商品同步任务 '''
    # try:
    #     store = Store.objects.get(id=store_detail["id"])
    # except BaseException:
    #     raise CustomException(10003)
    user_param = {}
    user_param["token"] = token
    end_stamp = time.time()
    start_stamp = end_stamp - common_params.MONTH_1 * 3
    total, error_msg = interface.get_wares(
        store_detail["platform_name"],
        user_param,
        store_detail,
        start_stamp,
        end_stamp,
        ware_detail_callback)
    if isinstance(error_msg, str):
        print(error_msg)
    # page_size = interface.get_product_pagesize(
    #     store.platform_name, store_detail)
    # if page_size is None or page_size == 0:
    #     page_size = common_params.PAGE_SIZE
    # pages = common_params.get_pages(goods_num, page_size)
    # start = time.time()
    # count = 0
    # for i in range(pages):
    #     pageno = i + 1
    #     product_page = interface.get_product_list(
    #         store.platform_name, store_detail, pageno)
    #     for product in product_page:
    #         sku_list = interface.to_oms_sku(
    #             store.platform_name, user_id, product)
    #         for item in sku_list:
    #             count += 1
    #             sku = Sku(**item)
    #             sku_old = Sku.objects.filter(item_code=item['item_code'])
    #             if sku_old:
    #                 sku_old.update(**item)
    #             else:
    #                 sku.id = IdGenerationService.generate_sku_id(user_id)
    #                 sku.save()
    # end = time.time()
    # headers = {'token': token}
    # url = str.format(
    #     "http://%s:%s/api/messages/put" %
    #     (settings.CMM['ip'], settings.CMM['port']))
    # msg = str.format("%s[%s]商品同步已完成，%s个商品共耗时%s秒" %
    #                  (store.store_name, store.username, count, end-start))
    # data = {
    #     "msg_type": 3,
    #     "msg_title": "商品同步完成通知",
    #     "msg_body": msg
    # }
    # try:
    #     resp = requests.post(url=url, headers=headers, data=data)
    #     res = json.loads(resp.text)
    #     if "error_code" not in res and res["error_code"] != 0:
    #         logging.warning("商品同步时发送消息返回失败，url:%s; return:%s" % (url, res))
    # except BaseException as e:
    #     logging.warning("商品同步时发送消息失败，error:%s" % (str(e)))
    # return True


@app.task
def refresh_token():
    TokenService().refresh()
    return 'success'


@app.task
def error_handler(uuid):
    print("------------------------")
    print(type(uuid), print(uuid))


@app.task
def cop_retry(url, headers, params, data, id=None):
    ''' COP重试 '''
    try:
        r = None
        method = json.loads(params)['method']  # 接口方法
        resp = requests.\
            post(url=url, headers=json.loads(headers),
                 params=json.loads(params),
                 data=data)
        if resp.headers['Content-Type'] == 'application/json':
            r = resp.json()
        elif resp.headers['Content-Type'] == 'text/xml':
            r = json.loads(json.dumps(xmltodict.parse(resp.text)))
        else:
            r = json.loads(json.dumps(xmltodict.parse(resp.text)))
        if r and int(r['response']['code']) == 0:
            handle_cop_result(r, method, id)
            return r
        else:
            handle_cop_result(r, method, id)
            logger.warn(r.text)
            raise Exception('Cop重试失败')
    except Exception as e:
        handle_cop_result(None, method, id)
        logger.warn(str(e))
        raise Exception('Cop重试失败')
    return ""


def handle_cop_result(result, method, id):
    ''' 处理Cop响应结果 '''
    if result['response']['flag'] == 'success':
        if method == 'taobao.qimen.deliveryorder.create':
            order = Order.objects.get(id=id)
            if 'deliveryOrderId' in result['response']:
                # 订单重试成功
                order.delivery_order_id = result['response']['deliveryOrderId']
                order.wms_status = 'ACCEPT'
                order.save()
            else:
                order.order_status = 80
                order.save()
        elif method == 'taobao.qimen.entryorder.create':
            stock_in = StockIn.objects.get(id=id)
            if 'entryOrderId' in result['response']:
                # 入库单重试成功
                stock_in.entry_order_id = result['response']['entryOrderId']
                stock_in.stock_in_status = 'ACCEPT'
                stock_in.save()
            else:
                stock_in.stock_in_status = 'EXCEPTION'
                stock_in.save()
