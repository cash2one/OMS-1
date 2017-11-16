#!/usr/bin/python3
#  -*- coding: utf-8 -*-
import json
import time
from uuid import uuid4
from oms_server.services.platforms import requests_util
from oms_server.services.platforms import common_params

# status_ori：
# 已付款，待发货：10
# 未付款，待发货：11
#
# 已发货：20
# 已部分发货：21
#
# 已签收：30
# 已部分签收：31
#
# 订单完成/关闭：-1
#
# refund_status_ori:
# 没有退款：0
# 全部退款成功：1
# 部分退款成功：2
# 退款关闭／拒绝：-1

DOMAIN = {
    "get_order": "https://api.vdian.com/api",
    "oauth": "https://api.vdian.com/token?grant_type=client_credential"
}


def refresh_token(store_detail, timeout=common_params.TIMEOUT):
    oauth = DOMAIN['oauth']
    url = oauth + '&appkey=' + store_detail['app_key'] + '&secret=' + store_detail['app_secret']
    resp = requests_util.get(url, timeout=timeout)
    res = json.loads(resp.text)
    status = res['status']
    access_token = None
    error_msg = None
    if status['status_code'] == 0:
        result = res['result']
        access_token = result['access_token']
        store_detail['access_token'] = access_token
        store_detail['expire_in'] = result['expire_in']
        store_detail['access_token'] = result['access_token']
    else:
        error_msg = res['status']['status_reason']
    return access_token, error_msg


def get_order_detail(store_detail, order_id):
    sys_params = {
        "method": "vdian.order.get",
        "access_token": store_detail["access_token"],
        "format": "json",
        "version": "1.0"
    }
    api_url = DOMAIN["get_order"]
    app_params = {"order_id": order_id}
    url = api_url + "?param=" + \
        json.dumps(app_params) + "&public=" + json.dumps(sys_params)
    resp = requests_util.get(url)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)

    detail = ""
    error_msg = None
    if "status" in res and "status_code" in res["status"]:
        if res["status"]["status_code"]:
            error_msg = res["status"]["status_reason"]
    if "result" in res:
        detail = res["result"]

    return detail, error_msg


def get_order_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize,
        order_type="all"):
    update_end = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(end_stamp))
    update_start = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    sys_params = {
        "method": "vdian.order.list.get",
        "access_token": store_detail["access_token"],
        "format": "json",
        "version": "1.2"
    }
    api_url = DOMAIN["get_order"]
    # order_type 订单类型，all：待发货；unpay：待付款；shiped：已发货；
    # refunding：退款中；finish：已完成；close：已关闭；all：全部类型
    app_params = {
        # "is_wei_order": 0,
        "page_num": pageno,
        "page_size": pagesize,
        "order_type": order_type,
        "update_start": update_start,
        "update_end": update_end,
    }
    url = api_url + "?param=" + \
        json.dumps(app_params) + "&public=" + json.dumps(sys_params)
    resp = requests_util.get(url)
    if not resp:
        return ""
    res = json.loads(resp.text)
    return res


def get_order_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_order_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize,
        "all")

    order_list = ""
    error_msg = None
    if "status" in res:
        if "status_code" in res["status"] and "status_reason" in res["status"]:
            if res["status"]["status_code"]:
                error_msg = res["status"]["status_reason"]
    if "result" in res and "orders" in res["result"]:
        order_list = res["result"]["orders"]

    return order_list, error_msg


def get_order_total(store_detail, start_stamp, end_stamp):
    res = get_order_response(
        store_detail,
        start_stamp,
        end_stamp,
        1,
        1,
        "all")
    error_msg = None
    total_num = 0
    if "status" in res:
        if "status_code" in res["status"] and "status_reason" in res["status"]:
            if res["status"]["status_code"]:
                error_msg = res["status"]["status_reason"]
    if "result" in res and "total_num" in res["result"]:
        if res["result"]["total_num"]:
            total_num = int(res["result"]["total_num"])
    return total_num, error_msg


# 商家确认退货
def accept_order_refund(store_detail, refund_no, refund_param):
    sys_params = {
        "method": "vdian.order.refund.accept",
        "access_token": store_detail["access_token"],
        "format": "json",
        "version": "1.1"
    }
    api_url = DOMAIN["get_order"]
    app_params = {"refund_no": refund_no}
    app_params.update(refund_param)
    url = api_url + "?param=" + \
        json.dumps(app_params) + "&public=" + json.dumps(sys_params)
    resp = requests_util.get(url)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    success = False
    error_msg = None
    if "status" in res:
        if "status_code" in res["status"] and "status_reason" in res["status"]:
            if res["status"]["status_code"]:
                error_msg = res["status"]["status_reason"]
        if "status_code" in res["status"] and res["status"]["status_code"] == 0:
            success = True
    return success, error_msg


def get_orders(
        user_param, store_detail,
        start_stamp, end_stamp, callback=None):
    total, error_msg = get_order_total(store_detail, start_stamp, end_stamp)
    # if total <= 0:
    #     return total, error_msg
    pagesize = common_params.PAGE_SIZE
    # print("订单总数为: ", total)
    pages = common_params.get_pages(total, pagesize)
    index = 0
    status = {}
    status["start_stamp"] = time.time()
    for i in range(pages):
        pageno = i + 1
        order_list, error_msg = get_order_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        if isinstance(error_msg, str) and len(error_msg):
            return total, error_msg
        for order in order_list:
            order_detail, error_msg = get_order_detail(
                store_detail, order["order_id"])
            if isinstance(error_msg, str) and len(error_msg):
                return total, error_msg
            oms_order = transfer_order(order_detail, common_params.get_short_name(__file__))
            if callback:
                if index == 0:
                    status["callback_status"] = "start"
                    status["start_stamp"] = time.time()
                else:
                    status["callback_status"] = "running"
                index += 1
                callback(user_param, store_detail, oms_order, index, status)
                time.sleep(0.01)
    if callback:
        status["callback_status"] = "end"
        status["end_stamp"] = time.time()
        callback(user_param, store_detail, None, index, status)
    return total, error_msg


def transfer_order(raw_order, prefix):
    order = {}

    order["order_id"] = str(uuid4())
    order["order_code_oms"] = prefix + "_" + str(raw_order["order_id"])

    # 1为货到付款，2为直接交易，3为担保交易
    order["order_type"] = raw_order["order_type"]
    order["order_code"] = str(raw_order["order_id"])
    order["total_price"] = raw_order["total"]
    order["goods_price"] = raw_order["price"]
    order["quantity"] = raw_order["quantity"]

    order["express_number"] = raw_order["express_no"]
    order["express_fee"] = raw_order["express_fee"]
    order["express_type"] = raw_order["express"]
    order["express_note"] = raw_order["express_note"]

    # status："订单oms状态"(10, "未审核"),(20, "已审核"),(30, "已签收"),(40,"已删除")
    order["status"] = 10
    order["order_status_info"] = ""

    order["status_ori"] = raw_order["status_ori"]
    order["refund_status_ori"] = raw_order["refund_status_ori"]

    # status_ori
    # 10:待付款
    # 20:已付款，待发货
    # 21:部分付款
    # 30:已发货
    # 31:部分发货
    # 40:已确认收货
    # 50:已完成
    # 60:已关闭

    # refund_status_ori
    # 0:没有退款
    # 1:退款中
    # 2:退款成功
    # 3:退款关闭

    order["buyer_note"] = raw_order["note"]
    order["seller_note"] = ""

    # 买家信息
    order["consignee_name"] = raw_order["buyer_info"]["name"]
    order["consignee_phone"] = raw_order["buyer_info"]["phone"]
    order["consignee_province"] = raw_order["buyer_info"]["province"]
    order["consignee_city"] = raw_order["buyer_info"]["city"]
    order["consignee_area"] = raw_order["buyer_info"]["region"]
    order["consignee_detail"] = raw_order["buyer_info"]["self_address"]

    order["pay_time"] = raw_order["pay_time"]  # 支付时间
    order["add_time"] = raw_order["add_time"]  # "下单时间

    # 转化订单详情
    order_details = []
    details = raw_order["items"]
    for detail in details:
        order_detail = {}
        order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
        order_detail["sku_id"] = ""  # detail["sku_id"]  # 商品型号ID
        order_detail["order_id"] = order["order_id"]
        order_detail["item_code"] = detail["sku_id"]    # detail["item_id"]  # 各平台id,可能重复
        order_detail["price"] = detail["price"]
        order_detail["quantity"] = int(detail["quantity"])
        order_detail["total_price"] = detail["total_price"]

        order_detail["is_gift"] = 0
        order_detail["is_exist"] = True

        order_details.append(order_detail)

    order["order_details"] = order_details

    # order_public = order_transfer_utils.get_public_info(
    #     oms_order["platform_id"],
    #     oms_order["store_id"],
    #     oms_order["user_id"],
    #     oms_order["store_is_auto_check"])
    #
    # for k in order_public:
    #     order[k] = order_public[k]
    return order


def get_ware_reponse(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize):
    update_start = time.strftime(
        "%Y-%m-%d%H:%M:%S",
        time.localtime(end_stamp))
    update_end = time.strftime(
        "%Y-%m-%d%H:%M:%S",
        time.localtime(start_stamp))
    sys_params = {
        "method": "vdian.item.list.get",
        "access_token": store_detail["access_token"],
        "format": "json",
        "version": "1.0",
    }
    # status = 1:或不传为在架商品，status = 2:为下架商品, 4:表示下架和在架商品
    app_params = {
        "page_num": pageno,
        "page_size": pagesize,
        "status": 1,
        "update_start": update_start,
        "update_end": update_end
    }
    api_url = DOMAIN["get_order"]
    url = api_url + "?param=" + \
        json.dumps(app_params) + "&public=" + json.dumps(sys_params)

    resp = requests_util.post(url)
    if not resp:
        return ""
    res = json.loads(resp.text)
    return res


def get_ware_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_ware_reponse(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize)

    ware_list = ""
    error_msg = None
    if "status" in res:
        if "status_code" in res["status"] and "status_reason" in res["status"]:
            if res["status"]["status_code"]:
                error_msg = res["status"]["status_reason"]
    if "result" in res and "items" in res["result"]:
        ware_list = res["result"]["items"]
    return ware_list, error_msg


def get_ware_total(store_detail, start_stamp, end_stamp):
    res = get_ware_reponse(store_detail, start_stamp, end_stamp, 1, 1)
    error_msg = None
    total_num = 0
    if "status" in res and "status_code" in res["status"]:
        error_msg = res["status"]["status_reason"]
    if "result" in res and "total_num" in res["result"]:
        if res["result"]["total_num"]:
            total_num = int(res["result"]["total_num"])
    return total_num, error_msg


def get_wares(user_param, store_detail,
              start_stamp, end_stamp, callback=None):
    total, error_msg = get_ware_total(store_detail, start_stamp, end_stamp)
    if total <= 0:
        return total, error_msg
    # print("商品总数为: ", total)
    pagesize = common_params.PAGE_SIZE
    pages = common_params.get_pages(total, pagesize)
    index = 0
    status = {}
    for i in range(pages):
        pageno = i + 1
        ware_list, error_msg = get_ware_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        if isinstance(error_msg, str) and len(error_msg):
            return total, error_msg
        for ware_detail in ware_list:
            sku_list = to_oms_sku(
                store_detail["user_id"], ware_detail)
            if isinstance(sku_list, list):
                for sku in sku_list:
                    if callback:
                        if index == 0:
                            status["callback_status"] = "start"
                            status["start_stamp"] = time.time()
                        index += 1
                        callback(user_param, store_detail, sku, total, index, status)
    if callback:
        status["callback_status"] = "end"
        status["end_stamp"] = time.time()
        callback(user_param, store_detail, None, total, index, status)
        return total, error_msg


def to_oms_sku(user_id, ware):
    # 无型号的商品skus为空
    skus = []
    if len(ware["skus"]) == 0:
        sku = {
            "user_id": str(user_id),
            "item_code": str(ware["itemid"]),
            "outer_item_code": "",
            "sku_name": str(ware["item_name"]),
            "specification": "",
            "bar_code": "",
            # "user_code": "",
            "price": float(ware["price"]),
            "unit": "",
            "goods_no": "",
            "sku_version": 0,
            "item_type": "",
            "brand": "",
            "brand_name": "",
            "color": "",
            "size": "",
            "gross_weight": 0,
            "net_weight": 0,
            "length": 0,
            "width": 0,
            "height": 0,
            "volume": 0,
            "pcs": 0,
            # "quantity": int(ware["stock"]),
            # "available_quantity": int(ware["stock"]),
            "is_shelflife": False,
            "lifecycle": 0,
            "reject_lifecycle": 0,
            "lockup_lifecycle": 0,
            "advent_lifecycle": 0,
            "is_sn_mgt": False,
            "is_hygroscopic": False,
            "is_danger": False
        }
        skus.append(sku)
    else:
        for item in ware['skus']:
            sku = {
                "user_id": str(user_id),
                "item_code": str(item["id"]),
                "outer_item_code": "",
                "sku_name": str(ware["item_name"] + item["title"]),
                "specification": "",
                "bar_code": "",
                # "user_code": "",
                "price": float(item["price"]),
                "unit": "",
                "goods_no": "",
                "sku_version": 0,
                "item_type": "",
                "brand": "",
                "brand_name": "",
                "color": "",
                "size": "",
                "gross_weight": 0,
                "net_weight": 0,
                "length": 0,
                "width": 0,
                "height": 0,
                "volume": 0,
                "pcs": 0,
                # "quantity": int(item["stock"]),
                # "available_quantity": int(item["stock"]),
                "is_shelflife": False,
                "lifecycle": 0,
                "reject_lifecycle": 0,
                "lockup_lifecycle": 0,
                "advent_lifecycle": 0,
                "is_sn_mgt": False,
                "is_hygroscopic": False,
                "is_danger": False
            }
            skus.append(sku)
    return skus


# 获取快递信息
def get_express_list(store_detail):
    sys_params = {
        "method": "vdian.order.expresslist",
        "access_token": store_detail["access_token"],
        "format": "json",
        "version": "1.0"
    }
    api_url = DOMAIN["get_order"]
    app_params = {}
    url = api_url + "?param=" + \
        json.dumps(app_params) + "&public=" + json.dumps(sys_params)
    resp = requests_util.get(url)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)

    express_list = {}
    error_msg = None
    if "status" in res:
        if "status_code" in res["status"] and "status_reason" in res["status"]:
            if res["status"]["status_code"]:
                error_msg = res["status"]["status_reason"]
    if "result" in res and "common_express" in res["result"]:
        express_info = res["result"]["common_express"]
        for item in express_info:
            express_list[item["express_company"]] = item

    return express_list, error_msg


# 订单发货处理 express_code：快递公司代码；deliver_no：快递单号；item_details 部分发货参数，不填为整单发货
def order_delivery(store_detail, order_id, express_code, deliver_no, item_details=None):
    express = transfer_express.get(express_code)
    if express is None:
        return False, "express_code is not found"
    if item_details:
        method = "vdian.order.deliver.split"
    else:
        method = "vdian.order.deliver"
    sys_params = {
        "method": method,
        "access_token": store_detail["access_token"],
        "format": "json",
        "version": "1.0"
    }
    api_url = DOMAIN["get_order"]
    app_params = {
        "express_no": deliver_no,
        "order_id": order_id,
        "express_type": express["id"],
        "express_custom": ""
    }
    skus = []
    if item_details:
        for item in item_details:
            if "item_id" in item and "item_sku_id" in item:
                if len(item["item_id"]) and len(item["item_sku_id"]):
                    sku = {}
                    sku["item_sku_id"] = item["item_sku_id"]
                    sku["item_id"] = item["item_id"]
                    skus.append(sku)
    if len(skus):
        app_params["items"] = skus
    url = api_url + "?param=" + \
        json.dumps(app_params) + "&public=" + json.dumps(sys_params)
    resp = requests_util.get(url)
    if not resp:
        return False, common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    success = False
    error_msg = None
    if "status" in res:
        if "status_code" in res["status"] and "status_reason" in res["status"]:
            if res["status"]["status_code"]:
                error_msg = res["status"]["status_reason"]
            else:
                success = True
    return success, error_msg


# # 订单部分发货处理 express_code：快递公司代码；deliver_no：快递单号；skus：sku列表
# def order_delivery_split(
#         store_detail, order_id, express_code,
#         deliver_no, item_details=None):
#     if express_code is None:
#         return False, "express_code is None"
#     if item_details:
#         method = "vdian.order.deliver.split"
#     else:
#         method = "vdian.order.deliver"
#     sys_params = {
#         "method": method,
#         "access_token": store_detail["access_token"],
#         "format": "json",
#         "version": "1.0"
#     }
#     api_url = DOMAIN["get_order"]
#     app_params = {
#         "express_no": deliver_no,
#         "order_id": order_id,
#         "express_type": express_code["id"],
#         "express_custom": "",
#         "items": item_details
#     }
#     url = api_url + "?param=" + \
#         json.dumps(app_params) + "&public=" + json.dumps(sys_params)
#     resp = requests_util.get(url)
#     if not resp:
#         return "", common_params.OBTAIN_DATA_FAILED
#     res = json.loads(resp.text)
#     success = False
#     error_msg = None
#     if "status" in res:
#         if "status_reason" in res["status"]:
#             error_msg = res["status"]["status_reason"]
#         if "status_code" in res["status"] and res["status"]["status_code"] == 0:
#             success = True
#     return success, error_msg


oms_express = {
    'SF': '顺丰',
    'EMS': '标准快递',
    'EYB': '经济快件',
    'ZJS': '宅急送',
    'YTO': '圆通',
    'ZTO': '中通(ZTO)',
    'HTKY': '百世汇通',
    'UC': '优速',
    'STO': '申通',
    'TTKDEX': '天天快递',
    'QFKD': '全峰',
    'FAST': '快捷',
    'POSTB': '邮政小包',
    'GTO': '国通',
    'YUNDA': '韵达',
    'JD': '京东配送',
    'DD': '当当宅配',
    'AMAZON': '亚马逊物流',
    'OTHER': '其他'
}

transfer_express = {
    # 顺丰
    'SF': {
        'id': 1,
        'express_company': '顺丰速运'
    },
    # 标准快递
    'EMS': {
        'id': 9,
        'express_company': 'EMS'
    },
    #
    'EYB': None,
    # 宅急送
    'ZJS': {
        'id': 7,
        'express_company': '宅急送'
    },
    # 圆通
    'YTO': {
        'id': 2,
        'express_company': '圆通速递'
    },
    # 中通(ZTO)
    'ZTO': {
        'id': 3,
        'express_company': '中通速递'
    },
    # 百世汇通
    'HTKY': {
        'id': 5,
        'express_company': '百世快递'
    },
    # 优速
    'UC': {
        'id': 22,
        'express_company': '优速快递'
    },
    #
    'STO': {
        'id': 4,
        'express_company': '申通快递'
    },
    # 天天快递
    'TTKDEX': {
        'id': 42975,
        'express_company': '天天快递'
    },
    # 全峰
    'QFKD': {
        'id': 20,
        'express_company': '全峰快递'
    },
    # 快捷
    'FAST': {
        'id': 23,
        'express_company': '快捷快递'
    },
    # 邮政小包
    'POSTB': {
        'id': 341539,
        'express_company': '邮政小包'
    },
    # 国通
    'GTO': {
        'id': 38248,
        'express_company': '国通快递'
    },
    # 韵达
    'YUNDA': {
        'id': 6,
        'express_company': '韵达快递'
    },
    # 京东配送
    'JD': {
        'id': 616246,
        'express_company': '京东快递'
    },
    # 当当宅配
    'DD': None,
    # 亚马逊物流
    'AMAZON': None
}


'''=========================test code========================='''


def order_detail_callback(store_id, store_detail, order_detail):
    if not order_detail:
        return
    oms_detail = {
        "store_id": store_id,
        "platform_name": store_detail["platform_name"],
        "user_id": store_detail["user_id"],
        "store_is_auto_check": store_detail["store_is_auto_check"]
    }
    order_detail.update(oms_detail)
    for item in order_detail["order_details"]:
        print(
            "商品编码=%s, 订单编号=%s, 买家手机=%s" %
            (item["item_code"],
             order_detail["consignee_phone"],
             order_detail["order_code"]))


def ware_detail_callback(user_param, sku, wares_total, sku_number, is_end):
    if is_end:
        print("共计%s个商品，%s个SKU" % (wares_total, sku_number))
    else:
        print(
            "商品编号 = %s, 商品名称 = %s 商品价格 = %s" %
            (sku["item_code"],
             sku["sku_name"],
             sku["price"]))


# TODO 测试
'''=========================test code========================='''
# store_detail = {
#     "app_key": "685719",
#     "app_secret": "a840c46a16c572a9b6c93e30f14dbaeb",
#     "access_token": "a07c18f7e27abae54aa9608bbfffa97a00076714de",
#     # "store_key": "48A29615B1F9A58A5E85",
#     "store_key": "",
#     "platform_name": "weidian",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }

store_detail = {
    "platform_id": 2,
    "platform_name": "weidian",
    "store_key": None,
    "store_name": "测试店铺",
    "app_key": "685338",
    "app_secret": "9a88ac61537de03945669d8b50193077",
    "access_token": "432a029a226448cd8f4da18c534a1b8100076332cd",
    "refresh_token": None,
    "id": "st1000000110001",
    "user_id": 10000001,
    "last_get_order_at": "2017-11-11 03:45:19",
    "store_is_auto_check": True,
}
# refresh_token(store_detail)

# store_id = "22a7a0f7b8ef4d44a016859237b03b0e"
# start_time = "2017-9-14 0:0:0"
# # end_time = "2017-9-11 0:0:0"
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# # # end_stamp = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()

# 测试获取订单
# get_orders(store_id, store_detail, start_stamp, end_stamp, order_detail_callback)

# 测试获取商品信息
# get_wares(store_detail, time.time(), common_params.DAY_90, ware_detail_callback)

# # 测试订单发货
order_id = '800378277341817'
get_order_detail(store_detail, order_id)
# order_detail, _ = get_order_detail(store_detail, order_id)
# oms_order = transfer_order(order_detail, common_params.get_short_name(__file__))
# express_list, ware_error_msg = get_express_list(store_detail)
# # print(express_list)
# express_name = "申通快递"
# deliver_no = "314672521551"
# express_code = "STO"
# item_details = []
# for item in oms_order["order_details"]:
#     sku = {
#         "item_id": item["item_code"],
#         "item_sku_id": item["sku_id"]
#     }
#     item_details.append(sku)
# # 在部分发货时，需要商品型号ID及该型号是否已发货，定义字段item_detail，is_delivered
# # 发货
# success, error_msg = order_delivery(store_detail, order_id, express_code, deliver_no, item_details=None)
#
# # 退款
# for item in order_detail["items"]:
#     if "refund_info" not in item:
#         continue
#     no = item["refund_info"]["refund_no"]
#     param = {
#         "is_accept": "2",    # 1：接受，2：拒绝
#         "refund_kind": "2",   # 1：表示退款，2：表示退货退款
#         "telephone": "13812345678",
#         "address": "青岛市",
#         "direct_refund": "0",    # 1:卖家选择直接退款退货（此时is_accept=1）；若不选择直接退款，则传0
#         "note": "卖家备注",
#         "refuse_reason": "拒绝原因",
#         "recipients": "收货人",
#     }
#     success, error_msg = accept_order_refund(store_detail, no, param)
# pass
