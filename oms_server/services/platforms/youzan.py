#!/usr/bin/python3
#  -*- coding: utf-8 -*-
import json
import time
from uuid import uuid4
from oms_server.services.platforms import requests_util
from oms_server.services.platforms import common_params

DOMAIN = {
    "get_order": "https://open.youzan.com/api/oauthentry/youzan.trades.sold/3.0.0/get",
    'get_order_detail': 'https://open.youzan.com/api/oauthentry/youzan.trade/3.0.0/get',
    "oauth": "https://open.youzan.com/oauth/token"}

# 有赞订单转化
order_status_pair = {
    # 没有创建支付交易
    "TRADE_NO_CREATE_PAY": 10,
    # 等待买家付款
    "WAIT_BUYER_PAY": 10,
    # 等待成团，即：买家已付款，等待成团
    "WAIT_GROUP": 10,

    # 等待卖家发货，即：买家已付款
    "WAIT_SELLER_SEND_GOODS": 20,

    # 等待买家确认收货，即：卖家已发货
    "WAIT_BUYER_CONFIRM_GOODS": 30,

    # 买家已签收
    "TRADE_BUYER_SIGNED": 40,

    # 付款以后用户退款成功，交易自动关闭
    "TRADE_CLOSED": 50,

    # 付款以前，卖家或买家主动关闭交易
    "TRADE_CLOSED_BY_USER": 60,
}

order_refund_status_pair = {
    # 无退款
    "NO_REFUND": 0,

    # 全额退款中
    "FULL_REFUNDING": 1,
    # 部分退款中
    "PARTIAL_REFUNDING": 11,

    # 已全额退款
    "FULL_REFUNDED": 2,
    # 已部分退款
    "PARTIAL_REFUNDED": 21,

    # 全额退款失败
    "FULL_REFUND_FAILED": 4,
    # 部分退款失败
    "PARTIAL_REFUND_FAILED": 41,
}


def refresh_token(store_detail, timeout=common_params.TIMEOUT):
    url = DOMAIN['oauth']
    params = {
        'content-type': 'application/x-www-form-urlencoded',
        'client_id': store_detail['app_key'],
        'client_secret': store_detail['app_secret'],
        'grant_type': 'silent',
        'kdt_id': store_detail['store_key']
    }
    resp = requests_util.post(url, data=params, timeout=timeout)
    res = json.loads(resp.text)
    access_token = None
    error_msg = None
    if "error_description" in res:
        error_msg = res["error_description"]
    if "access_token" in res:
        access_token = res['access_token']
        store_detail['expire_in'] = res['expires_in']
        store_detail['access_token'] = res['access_token']
    return access_token, error_msg


def get_order_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    if end_stamp - start_stamp > common_params.MONTH_3:
        start_stamp = end_stamp - common_params.MONTH_3
    url = DOMAIN["get_order"]
    update_end = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(end_stamp))
    update_start = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    params = {
        "access_token": store_detail["access_token"],
        "start_update": update_start,
        "end_update": update_end,
        "page_no": pageno,
        "page_size": pagesize,
        "type": "all",
    }
    resp = requests_util.get(url=url, params=params)
    res = json.loads(resp.text)
    order_list = ""
    error_msg = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res:
        if "trades" in res["response"]:
            order_list = res["response"]["trades"]
    return order_list, error_msg


def get_order_total(store_detail, start_stamp, end_stamp):
    if end_stamp - start_stamp > common_params.MONTH_3:
        start_stamp = end_stamp - common_params.MONTH_3
    url = DOMAIN["get_order"]
    update_end = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(end_stamp))
    update_start = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    params = {
        "access_token": store_detail["access_token"],
        "start_update": update_start,
        "end_update": update_end,
        "page_no": 1,
        "page_size": 1,
        "type": "all",
    }
    resp = requests_util.get(url=url, params=params)
    res = json.loads(resp.text)
    total_num = 0
    error_msg = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res:
        if "trades" in res["response"]:
            total_num = int(res["response"]["total_results"])
    return total_num, error_msg


def get_order_detail(store_detail, order_id):
    url = DOMAIN["get_order_detail"]
    params = {
        "access_token": store_detail["access_token"],
        "tid": order_id
    }
    resp = requests_util.get(url=url, params=params)
    res = json.loads(resp.text)
    detail = ""
    error_msg = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res and "trade" in res["response"]:
        detail = res["response"]["trade"]
    return detail, error_msg


def get_orders(store_id, store_detail, start_stamp, end_stamp, callback=None):
    total, error_msg = get_order_total(store_detail, start_stamp, end_stamp)
    if total <= 0:
        return
    pagesize = common_params.PAGE_SIZE
    print("订单总数为: ", total)
    pages = common_params.get_pages(total, pagesize)
    start_timestamp = time.time()
    for i in range(pages):
        pageno = i + 1
        order_list, error_msg = get_order_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        for order in order_list:
            order_detail, error_msg = get_order_detail(
                store_detail, order["tid"])
            oms_order = transfer_order(
                order_detail, common_params.get_short_name(__file__))
            if callback:
                callback(store_id, store_detail, oms_order)
    end_timestamp = time.time()
    span = end_timestamp - start_timestamp
    print("耗时%s秒" % span)


# 有赞订单转化
def transfer_order(raw_order, prefix):
    order = {}

    order["order_id"] = str(uuid4())
    order["order_code_oms"] = prefix + "_" + str(raw_order["tid"])
    order["order_type"] = raw_order["type"]  # 交易类型
    order["order_code"] = raw_order["tid"]  # 交易编号
    order["total_price"] = raw_order["total_fee"]  # 总价格
    order["goods_price"] = raw_order["price"]  # 商品单价
    order["quantity"] = raw_order["num"]  # 商品数量

    order["express_number"] = ""
    order["express_fee"] = 0

    # 物流方式 取值范围：express（快递），fetch（到店自提），local（同城配送）
    order["express_type"] = raw_order["shipping_type"]
    order["express_note"] = ""

    # status："订单oms状态"(10, "未审核"),(20, "已审核"),(30, "已签收"),(40,"已删除")
    order["status"] = 10
    order["order_status_info"] = ""

    # status："订单oms状态"(10, "未审核"),(20, "已审核"),(30, "已签收"),
    order["status_ori"] = order_status_pair[raw_order["status"]]  # 订单状态 枚举值
    order["refund_status_ori"] = order_refund_status_pair[raw_order["refund_state"]]  # 退款状态

    order["buyer_note"] = raw_order["buyer_message"]  # 买家留言
    order["seller_note"] = raw_order["trade_memo"]  # 卖家备注

    # 买家信息
    order["consignee_name"] = raw_order["receiver_name"]        #
    order["consignee_phone"] = raw_order["receiver_mobile"]  # 电话
    order["consignee_province"] = raw_order["receiver_state"]  # 省份
    order["consignee_city"] = raw_order["receiver_city"]  # 城市
    order["consignee_area"] = raw_order["receiver_district"]  # 地区
    order["consignee_detail"] = raw_order["receiver_address"]  # 地址

    order["pay_time"] = raw_order["pay_time"]  # 支付时间
    order["add_time"] = raw_order["created"]  # "下单时间

    # 转化订单详情
    order_details = []
    details = raw_order["orders"]
    for detail in details:
        order_detail = {}
        order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
        # 交易明细编号。该编号并不唯一，只用于区分交易内的多条明细记录
        order_detail["sku_id"] = detail["oid"]
        order_detail["order_id"] = order["order_id"]  # 订单编号
        order_detail["item_code"] = detail["item_id"]  # 交易明细编号
        order_detail["price"] = detail["price"]
        order_detail["quantity"] = int(detail["num"])
        order_detail["total_price"] = detail["payment"]  # 应付金额

        order_detail["is_gift"] = 0
        order_detail["is_exist"] = True

        order_details.append(order_detail)

    order["order_details"] = order_details

    # order_public = order_transfer_utils.get_public_info(
    #     oms_order["platform_id"],
    #     oms_order["store_id"],
    #     oms_order["user_id"],
    #     oms_order["store_is_auto_check"])

    # for k in order_public:
    #     order[k] = order_public[k]

    return order


def get_ware_detail(store_detail, ware_id):
    url = "https://open.youzan.com/api/oauthentry/youzan.item/3.0.0/get"
    params = {
        "access_token": store_detail["access_token"],
        "item_id": ware_id,
    }
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return ""
    res = json.loads(resp.text)
    error_msg = None
    ware_detail = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res and "item" in res["response"]:
        ware_detail = res["response"]["item"]
    return ware_detail, error_msg


def get_ware_reponse(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize):
    url = "https://open.youzan.com/api/oauthentry/youzan.items.onsale/3.0.0/get"
    params = {
        "access_token": store_detail["access_token"],
        "page_no": pageno,
        "page_size": pagesize,
    }
    resp = requests_util.get(url=url, params=params)
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
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res and "items" in res["response"]:
        ware_list = res["response"]["items"]

    return ware_list, error_msg
    # return ware_list


def get_ware_total(store_detail, start_stamp, end_stamp):
    res = get_ware_reponse(store_detail, start_stamp, end_stamp, 1, 1)
    total_num = 0
    error_msg = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res and "count" in res["response"]:
        if res["response"]["count"]:
            total_num = int(res["response"]["count"])
    # return total_num
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
        for ware in ware_list:
            ware_detail, error_msg = get_ware_detail(store_detail, ware["item_id"])
            if isinstance(error_msg, str) and len(error_msg):
                return total, error_msg
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
    skus = []
    if len(ware["skus"]) == 0:
        sku = {
            "user_id": str(user_id),
            "item_code": str(ware['item_id']),
            "outer_item_code": "",
            "sku_name": str(ware['title']),
            "specification": "",
            "bar_code": "",
            # "user_code": "",
            "price": ware["price"] / 100,
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
            # "quantity": quantity,
            # "available_quantity": quantity,
            "is_shelflife": False,
            "lifecycle": 0,
            "reject_lifecycle": 0,
            "lockup_lifecycle": 0,
            "advent_lifecycle": 0,
            "is_sn_mgt": False,
            "is_hygroscopic": False,
            "is_danger": False
        }
        # 商家编码，商家给商品设置的商家编码
        if len(ware['item_no']):
            sku["item_code"] = ware["item_no"]
        skus.append(sku)
    else:
        for item in ware['skus']:
            sku = {
                "user_id": str(user_id),
                "item_code": str(item["sku_id"]),
                "outer_item_code": "",
                "sku_name": str(ware["item_name"] + item["sku_id"]),
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
    url = "https://open.youzan.com/api/oauthentry/youzan.logistics.express/3.0.0/get"
    params = {
        "access_token": store_detail["access_token"],
    }
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return ""
    res = json.loads(resp.text)
    express_list = {}
    error_msg = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res and "allExpress" in res["response"]:
        express_list = res["response"]["allExpress"]
    return express_list, error_msg


# 订单部分发货处理 express_code：快递公司代码；deliver_no：快递单号；skus：sku列表
def order_delivery(store_detail, order_id,
                   express_code, deliver_no, item_details=None):
    express = transfer_express.get(express_code)
    if express is None:
        return False, "express_code is not found"

    url = "https://open.youzan.com/api/oauthentry/youzan.logistics.online/3.0.0/confirm"
    skus = None
    if item_details:
        for item in item_details:
            if skus:
                skus += "," + str(item)
            else:
                skus = str(item)
    app_params = {
        "access_token": store_detail["access_token"],
        "tid": order_id,
        "oids": skus,
        "out_stype": express["id"],
        "out_sid": deliver_no,
    }
    resp = requests_util.get(url=url, params=app_params)
    if not resp:
        return False, common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    success = False
    error_msg = None
    if "error_response" in res and "msg" in res["error_response"]:
        error_msg = res["error_response"]["msg"]
    if "response" in res and "is_success" in res["response"]:
        success = res["response"]["is_success"]
    return success, error_msg


transfer_express = {
    # 顺丰
    'SF': {
        'id': 7,
        'express_company': '顺丰速运'
    },
    # 标准快递
    'EMS': {
        'id': 11,
        'express_company': 'EMS'
    },
    #
    'EYB': {
        'id': 10,
        'express_company': 'EMS经济快递'
    },
    # 宅急送
    'ZJS': {
        'id': 25,
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
        'id': 6,
        'express_company': '百世快递'
    },
    # 优速
    'UC': {
        'id': 38,
        'express_company': '优速快递'
    },
    #
    'STO': {
        'id': 1,
        'express_company': '申通E物流'
    },
    # 天天快递
    'TTKDEX': {
        'id': 5,
        'express_company': '天天快递'
    },
    # 全峰
    'QFKD': {
        'id': 17,
        'express_company': '全峰快递'
    },
    # 快捷
    'FAST': {
        'id': 34,
        'express_company': '快捷速递'
    },
    # 邮政小包
    'POSTB': {
        'id': 8,
        'express_company': '邮政国内小包'
    },
    # 国通
    'GTO': {
        'id': 40,
        'express_company': '国通快递'
    },
    # 韵达
    'YUNDA': {
        'id': 4,
        'express_company': '韵达快运'
    },
    # 京东配送
    'JD': {
        'id': 138,
        'express_company': '京东快递'
    },
    # 当当宅配
    'DD': {
        'id': 181,
        'express_company': '当当物流'
    },
    # 亚马逊物流
    'AMAZON': {
        'id': 137,
        'express_company': '亚马逊物流'
    },
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


def ware_detail_callback(store_id, store_detail, ware_detail):
    if not ware_detail:
        return
    for item in ware_detail:
        print(
            "商品编码=%s, 商品名称=%s, 商品价格=%s" %
            (item["item_code"],
             item["sku_name"],
             item["price"]))


# TODO 测试
'''=========================test code========================='''
# store_detail = {
#     "app_key": "c59d6819e6ccccac381",
#     "app_secret": "99779bea68051ce8fd84164a2bbc2113",
#     "access_token": "61abf9405f2d3688ab63ff427df1fd1a",
#     "store_key": "19378592",
#     "expire_in": "",
#     "platform_name": "youzan",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }
# store_detail = {
#     "app_key": "c59d6819e6ccccac38",
#     "app_secret": "99779bea68051ce8fd84164a2bbc2113",
#     "access_token": "8ad018f6b85934f59d473f0d7ca4d181",
#     "store_key": "19378592",
#     "platform_name": "youzan",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }

# refresh_token(store_detail)
# store_id = "1ab3334d-d57f-4dcb-9c7c-68d3afdcc88d"
#
# start_time = "2017-9-22 0:0:0"
# end_time = "2017-9-28 0:0:0"
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()
#
# # 获取订单
# get_orders(
#     store_id,
#     store_detail,
#     start_stamp,
#     end_stamp,
#     order_detail_callback)
# order_id = "E20171015202427076400005"
# order, _ = get_order_detail(store_detail, order_id)
# oms_order = transfer_order(order, common_params.get_short_name(__file__))
# # 发货
# express_list, _ = get_express_list(store_detail)
# express_name = "申通快递"
# deliver_no = "314672521551"
# express_code = "STO"
# # express_list.get(express_name, None)
# # express_list = get_express_list(store_detail)
# skus = []
# for item in oms_order["order_details"]:
#     sku = item["sku_id"]
#     skus.append(sku)
# order_delivery(store_detail, oms_order["order_code"], express_code, deliver_no, item_details=skus)
# # 获取商品信息
# get_wares(store_id, store_detail, time.time(), common_params.DAY_90, ware_detail_callback)
