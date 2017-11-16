#!/usr/bin/python3
#  -*- coding: utf-8 -*-

# 拼多多接口

import time
import json
from uuid import uuid4
from oms_server.services.platforms import requests_util
from hashlib import md5
from oms_server.services.platforms import common_params


DOMAIN = {
    "api": "http://open.yangkeduo.com/api/router?",
}


is_full_query = True


order_status_pair = {
    # 等待发货
    '1': 20,

    # 已发货
    '2': 30,

    # 交易成功
    '3': 40
}

order_refund_status_pair = {
    # 无售后货售后关闭
    "1": 0,

    # 售后处理中
    "2": 1,

    # 退款中
    "3": 1,

    # 退款成功
    "4": 2
}


def refresh_token(store_detail, timeout=common_params.TIMEOUT):
    return None, None


def get_order_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    api_params = {
        "type": "pdd.order.number.list.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime()))),

        "order_status": 1,  # 1：待发货，2：已发货待签收，3：已签收 5：全部 暂时只开放待发货订单查询
        "page": pageno,
        "page_size": pagesize
    }
    order_api = API(DOMAIN["api"], api_params, store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    error_msg = ""
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
    order_list = ""
    if "order_sn_list_get_response" in res:
        if "order_sn_list" in res["order_sn_list_get_response"]:
            order_list = res["order_sn_list_get_response"]["order_sn_list"]
    return order_list, error_msg


def get_increment_order_list(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize):
    start_stamp = end_stamp - 30 * 60
    api_params = {
        "type": "pdd.order.number.list.increment.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime()))),

        "order_status": 5,  # 1：待发货，2：已发货待签收，3：已签收 5：全部
        "page": pageno,
        "page_size": pagesize,
        "is_lucky_flag": 1,
        "refund_status": 5,
        "start_updated_at": int(start_stamp),
        "end_updated_at": int(end_stamp),
    }
    order_api = API(DOMAIN["api"], api_params, store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    error_msg = ""
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
    order_list = ""
    if "order_sn_increment_get_response" in res:
        if "order_sn_list" in res["order_sn_increment_get_response"]:
            order_list = res["order_sn_increment_get_response"]["order_sn_list"]
    return order_list, error_msg


def get_order_detail(store_detail, order_id):
    api_params = {
        "type": "pdd.order.information.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime()))),

        "order_sn": order_id
    }
    order_api = API(
        DOMAIN["api"],
        api_params,
        store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    error_msg = ""
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
    detail = ""
    if "order_info_get_response" in res:
        if "order_info" in res["order_info_get_response"]:
            detail = res["order_info_get_response"]["order_info"]
    return detail, error_msg


def get_orders(
        user_param, store_detail,
        start_stamp, end_stamp, callback=None):
    global is_full_query
    pagesize = common_params.PAGE_SIZE
    index = 0
    status = {}
    status["start_stamp"] = time.time()
    if is_full_query:
        is_full_query = False
        pageno = 0
        while True:
            pageno += 1
            order_list, error_msg = get_order_list(
                store_detail, start_stamp, end_stamp, pageno, pagesize)
            if len(order_list) == 0 or len(error_msg):
                break
            if isinstance(error_msg, str) and len(error_msg):
                return index, error_msg
            for order in order_list:
                order_detail, error_msg = get_order_detail(
                    store_detail, order["order_sn"])
                if isinstance(error_msg, str) and len(error_msg):
                    return index, error_msg
                oms_order = transfer_order(order_detail, common_params.get_short_name(__file__))
                if callback:
                    if index == 0:
                        status["callback_status"] = "start"
                        status["start_stamp"] = time.time()
                    else:
                        status["callback_status"] = "running"
                    index += 1
                    callback(user_param, store_detail, oms_order, index, status)
    pageno = 0
    while True:
        pageno += 1
        order_list, error_msg = get_increment_order_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        if len(order_list) == 0 or len(error_msg):
            break
        if isinstance(error_msg, str) and len(error_msg):
            return index, error_msg
        for order in order_list:
            order_detail, error_msg = get_order_detail(
                store_detail, order["order_sn"])
            if isinstance(error_msg, str) and len(error_msg):
                return index, error_msg
            oms_order = transfer_order(order_detail, common_params.get_short_name(__file__))
            if callback:
                if index == 0:
                    status["callback_status"] = "start"
                    status["start_stamp"] = time.time()
                else:
                    status["callback_status"] = "running"
                index += 1
                callback(user_param, store_detail, oms_order, index, status)
    if callback:
        status["callback_status"] = "end"
        status["end_stamp"] = time.time()
        callback(user_param, store_detail, None, index, status)
    return index, error_msg


# 拼多多订单转化
def transfer_order(raw_order, prefix):
    order = {}

    order["order_id"] = str(uuid4())
    order["order_code_oms"] = prefix + "_" + str(raw_order["order_sn"])

    order["order_type"] = raw_order["pay_type"]     # 支付方式 QQ，WEIXIN,ALIPAY
    order["order_code"] = raw_order["order_sn"]  # 交易编号
    order["total_price"] = raw_order["goods_amount"]  # 总价格
    order["goods_price"] = raw_order["goods_amount"]  # 商品单价
    order["quantity"] = "1"  # 商品数量

    order["express_number"] = raw_order["tracking_number"]  # 快递编号
    order["express_fee"] = float(raw_order["postage"])      # 快递费
    order["express_type"] = raw_order["logistics_id"]   # 快递公司编号
    order["express_note"] = ""

    # 物流方式 取值范围：express（快递），fetch（到店自提），local（同城配送）
    order["express_type"] = ""

    # status："订单oms状态"(10, "未审核"),(20, "已审核"),(30, "已签收"),
    order["status"] = 10
    order["order_status_info"] = ""

    order["status_ori"] = order_status_pair[str(
        raw_order["order_status"])]  # 订单状态 枚举值
    order["refund_status_ori"] = order_refund_status_pair[str(
        raw_order["refund_status"])]  # 退款状态

    order["buyer_note"] = raw_order["remark"]  # 买家留言
    order["seller_note"] = ""  # 卖家备注

    # 买家信息
    order["consignee_name"] = raw_order["receiver_name"]        #
    order["consignee_phone"] = raw_order["receiver_phone"]  # 电话
    order["consignee_country"] = raw_order["country"]  # 国家
    order["consignee_province"] = raw_order["province"]  # 省份
    order["consignee_city"] = raw_order["city"]  # 城市
    order["consignee_area"] = raw_order["town"]  # 地区
    order["consignee_detail"] = raw_order["address"]  # 地址

    order["pay_time"] = raw_order["confirm_time"]  # 成团时间
    order["add_time"] = raw_order["created_time"]  # 下单时间

    # 转化订单详情
    order_details = []
    details = raw_order["item_list"]
    for detail in details:
        order_detail = {}
        order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
        order_detail["sku_id"] = detail["sku_id"]  # str(uuid1())
        order_detail["order_id"] = order["order_id"]  # 订单编号
        order_detail["item_code"] = detail["sku_id"]  # 交易明细编号
        order_detail["price"] = float(detail["goods_price"])
        order_detail["quantity"] = int(detail["goods_count"])
        order_detail["total_price"] = detail["goods_count"] * \
            detail["goods_price"]

        order_detail["is_gift"] = 0   # 是否赠品
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


def get_ware_detail(store_detail, goods_id):
    sys_params = {
        "type": "pdd.goods.information.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime())))
    }
    app_params = {
        "goods_id": goods_id
    }
    params = sys_params.copy()
    params.update(app_params)
    order_api = API(
        DOMAIN["api"],
        params,
        store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    error_msg = ""
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
    ware_detail = ""
    if "goods_info_get_response" in res:
        if "goods_info" in res["goods_info_get_response"]:
            ware_detail = res["goods_info_get_response"]["goods_info"]
    return ware_detail, error_msg


def get_ware_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    sys_params = {
        "type": "pdd.goods.list.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime())))
    }
    app_params = {
        "page": pageno,
        "page_size": pagesize
    }
    params = sys_params.copy()
    params.update(app_params)
    order_api = API(
        DOMAIN["api"],
        params,
        store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    ware_list = ""
    error_msg = None
    if "goods_list_get_response" in res:
        if "goods_list" in res["goods_list_get_response"]:
            ware_list = res["goods_list_get_response"]["goods_list"]
    return ware_list, error_msg


def get_ware_total(store_detail, start_stamp, end_stamp):
    sys_params = {
        "type": "pdd.goods.list.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime())))
    }
    app_params = {
        "page": 1,
        "page_size": 1
    }
    params = sys_params.copy()
    params.update(app_params)
    order_api = API(
        DOMAIN["api"],
        params,
        store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    total_num = 0
    error_msg = None
    if "goods_list_get_response" in res:
        if "total_count" in res["goods_list_get_response"]:
            total_num = res["goods_list_get_response"]["total_count"]
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
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


# 同一个商品ID下可以有多个sku
def to_oms_sku(user_id, ware):
    skus = []
    for item in ware['sku_list']:
        sku = {
            "user_id": str(user_id),
            "item_code": str(item['sku_id']),
            # "outer_item_code": ware["outer_id"],
            "sku_name": str(ware['goods_name']) + item["spec"],
            "specification": item["spec"],
            "bar_code": "",
            # "user_code": "",
            "price": 0.0,
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
            # "quantity": int(item['sku_quantity']),
            # "available_quantity": int(item['sku_quantity']),
            "is_shelflife": False,
            "lifecycle": 0,
            "reject_lifecycle": 0,
            "lockup_lifecycle": 0,
            "advent_lifecycle": 0,
            "is_sn_mgt": False,
            "is_hygroscopic": False,
            "is_danger": False
        }
        # 商家编码SKU维度
        # if len(item["outer_id"]):
        #     sku["item_code"] = item["outer_id"]
        skus.append(sku)
    return skus


class API:
    request_params = {}
    app_secret = ""
    api = ""

    def __init__(self, api, param, app_secret):
        self.api = api
        self.request_params = param
        self.app_secret = app_secret

    # 生成签名和请求的url
    def make_sign(self):
        from hashlib import md5
        keys = sorted(self.request_params.keys())
        md5_str = self.app_secret
        api_url = ""
        for key in keys:
            md5_str += key
            md5_str += str(self.request_params[key])
            if key is not 'type':
                if api_url:
                    api_url += ('&' + key + '=' +
                                str(self.request_params[key]))
                else:
                    api_url += (key + '=' + str(self.request_params[key]))
        md5_str += self.app_secret

        sign_hash = md5()
        sign_hash.update(md5_str.encode())
        sign = sign_hash.hexdigest().upper()
        self.request_params['sign'] = sign

        url = self.api + 'type=' + \
            self.request_params['type'] + '&sign=' + sign + '&' + api_url
        # url = self.api + api_url + '&sign=' + sign
        return url

    # 发送请求
    def request(self):
        request_url = self.make_sign()
        response = requests_util.post(request_url)
        return response


# 获取快递信息
def get_express_list(store_detail):
    sys_params = {
        "type": "pdd.logistics.companies.get",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime())))
    }
    app_params = {}
    params = sys_params.copy()
    params.update(app_params)
    order_api = API(
        DOMAIN["api"],
        params,
        store_detail["app_secret"])
    resp = order_api.request()

    res = json.loads(resp.text)
    express_list = {}
    error_msg = ""
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
    if "logistics_companies_get_response" in res and "logistics_companies" in res[
            "logistics_companies_get_response"]:
        express_info = res["logistics_companies_get_response"]["logistics_companies"]
        for item in express_info:
            express_list[item["logistics_company"]] = item
    return express_list, error_msg


# 订单发货处理 express_code：快递公司代码；deliver_no：快递单号；
def order_delivery(store_detail, order_id, express_code, deliver_no, item_details=None):
    express = transfer_express.get(express_code)
    if express is None:
        return False, "express_code is not found"
    sys_params = {
        "type": "pdd.logistics.online.send",
        "mall_id": store_detail["app_key"],
        "data_type": "JSON",
        "version": "V1",
        "timestamp": str(int(time.mktime(time.localtime())))
    }
    app_params = {
        "order_sn": order_id,
        "logistics_id": express["id"],
        "tracking_number": deliver_no
    }
    params = sys_params.copy()
    params.update(app_params)
    order_api = API(
        DOMAIN["api"],
        params,
        store_detail["app_secret"])
    resp = order_api.request()
    if not resp:
        return False, common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    success = False
    error_msg = ""
    if "error_response" in res and "error_msg" in res["error_response"]:
        error_msg = res["error_response"]["error_msg"]
    if "logistics_online_send_response" in res:
        if "is_success" in res["logistics_online_send_response"]:
            if res["logistics_online_send_response"]["is_success"] == "1":
                success = True
    return success, error_msg


transfer_express = {
    # 顺丰
    'SF': {
        'id': 44,
        'express_company': '顺丰速运'
    },
    # 标准快递
    'EMS': {
        'id': 118,
        'express_company': 'EMS'
    },
    #
    'EYB': None,
    # 宅急送
    'ZJS': {
        'id': 129,
        'express_company': '宅急送'
    },
    # 圆通
    'YTO': {
        'id': 85,
        'express_company': '圆通速递'
    },
    # 中通(ZTO)
    'ZTO': {
        'id': 115,
        'express_company': '中通速递'
    },
    # 百世汇通
    'HTKY': {
        'id': 229,
        'express_company': '百世快递'
    },
    # 优速
    'UC': {
        'id': 117,
        'express_company': '优速快递'
    },
    #
    'STO': {
        'id': 1,
        'express_company': '申通快递'
    },
    # 天天快递
    'TTKDEX': {
        'id': 119,
        'express_company': '天天快递'
    },
    # 全峰
    'QFKD': {
        'id': 116,
        'express_company': '全峰快递'
    },
    # 快捷
    'FAST': {
        'id': 122,
        'express_company': '快捷快递'
    },
    # 邮政小包
    'POSTB': {
        'id': 132,
        'express_company': '邮政快递包裹'
    },
    # 国通
    'GTO': {
        'id': 124,
        'express_company': '国通快递'
    },
    # 韵达
    'YUNDA': {
        'id': 121,
        'express_company': '韵达快递'
    },
    # 京东配送
    'JD': {
        'id': 120,
        'express_company': '京东快递'
    },
    # 当当宅配
    'DD': None,
    # 亚马逊物流
    'AMAZON': {
        'id': 156,
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
#     "app_key": "233439",
#     "app_secret": "BFC6800FEEC6DC6D18DE9DB13B72BDBC",
#     "access_token": "",
#     # "store_key": "48A29615B1F9A58A5E85",
#     "store_key": "",
#     "platform_name": "pinduoduo",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }
# store_detail["access_token"] = get_token(store_detail)
# store_id = "1ab3334d-d57f-4dcb-9c7c-68d3afdcc88d"
#
# start_time = "2017-9-22 0:0:0"
# # end_time = "2017-9-28 0:0:0"
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()
# end_stamp = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))

# get_order_list(store_detail, start_stamp, end_stamp, 1, 1)
# get_increment_order_list(store_detail, start_stamp, end_stamp, 1, 1)

# 测试获取订单
# get_orders(store_id, store_detail, start_stamp, end_stamp, order_detail_callback)

# 测试获取商品信息
# get_wares(store_id, store_detail, start_stamp, end_stamp, ware_detail_callback)

# # 测试订单发货
# order_id = '800170211512979'
# express_list, ware_error_msg = get_express_list(store_detail)
# express_name = "申通快递"
# deliver_no = "314672521551"
# express_code = "STO"
# success, error_msg = order_delivery(store_detail, order_id, express_code, deliver_no)
