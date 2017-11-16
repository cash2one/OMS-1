#!/usr/bin/python3
#  -*- coding: utf-8 -*-

import json
import time
from uuid import uuid4
from hashlib import md5
from oms_server.services.platforms import requests_util
from oms_server.services.platforms import common_params

DOMAIN = {
    "api": "https://api.jd.com/routerjson?",
    "oauth": "https://oauth.jd.com/oauth/token?"
}


def refresh_token(store_detail, timeout=common_params.TIMEOUT):
    url = DOMAIN.get("oauth", "")
    data = {
        "grant_type": "refresh_token",
        "client_id": store_detail["app_key"],
        "client_secret": store_detail["app_secret"],
        "refresh_token": store_detail["refresh_token"]
    }
    resp = requests_util.post(url, data=data, timeout=timeout)
    res = json.loads(resp.text)
    error_msg = None
    access_token = None
    if "access_token" in res:
        access_token = res["access_token"]
    if "error_description" in res:
        error_msg = res["error_description"]
    return access_token, error_msg


# order_state，多订单状态可以用英文逗号隔开
# 1）WAIT_SELLER_STOCK_OUT 等待出库
# 2）WAIT_GOODS_RECEIVE_CONFIRM 等待确认收货
# 3）WAIT_SELLER_DELIVERY 等待发货（只适用于海外购商家，含义为'等待境内发货'标签下的订单,非海外购商家无需使用）
# 4) PAUSE 暂停（loc订单可通过此状态获取）
# 5）FINISHED_L 完成
# 6）TRADE_CANCELED 取消
# 7）LOCKED 已锁定
def get_order_detail(store_detail, order_id):
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    sys_params = {
        "method": "jingdong.pop.order.get",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    app_params = {
        "order_id": order_id,
        # "order_state": "WAIT_SELLER_STOCK_OUT,WAIT_GOODS_RECEIVE_CONFIRM,"
        #                "WAIT_SELLER_DELIVERY,FINISHED_L,TRADE_CANCELED",
        "optional_fields": "orderId,orderType,payType,orderTotalPrice,orderSellerPrice,orderPayment,"
                           "freightPrice,orderState,orderStateRemark,deliveryType,orderRemark,orderStartTime,"
                           "consigneeInfo,itemInfoList,venderRemark,returnOrder,paymentConfirmTime,waybill,"
                           "logisticsId,modified",
    }
    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return ""
    res = json.loads(resp)

    detail = ""
    error_msg = None
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_pop_order_get_responce" in res:
        responce = res["jingdong_pop_order_get_responce"]
        if "orderDetailInfo" in responce \
                and "apiResult" in responce["orderDetailInfo"]:
            api_result = responce["orderDetailInfo"]["apiResult"]
            if api_result["success"] is not True:
                error_msg = api_result["chineseErrCode"]
        if "orderDetailInfo" in responce \
                and "orderInfo" in responce["orderDetailInfo"]:
            detail = responce["orderDetailInfo"]["orderInfo"]

    return detail, error_msg


def get_order_response(store_detail, start_stamp, end_stamp, pageno, pagesize):
    if start_stamp < end_stamp - common_params.MONTH_1:
        start_stamp = end_stamp - common_params.MONTH_1
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    end_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_stamp))
    start_date = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    sys_params = {
        "method": "jingdong.pop.order.search",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    app_params = {
        "start_date": start_date,
        "end_date": end_date,
        # "order_state": "4,5,6",
        "order_state": "WAIT_SELLER_STOCK_OUT,WAIT_GOODS_RECEIVE_CONFIRM,"
                       "WAIT_SELLER_DELIVERY,FINISHED_L,TRADE_CANCELED",
        "page": pageno,
        "page_size": pagesize,
        "optional_fields": "orderId"
        # optional_fields 是否有默认值？
    }

    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return ""
    res = json.loads(resp)
    return res


def get_order_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_order_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize)
    order_list = ""
    error_msg = None
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_pop_order_search_responce" in res:
        responce = res["jingdong_pop_order_search_responce"]
        if "searchorderinfo_result" in responce \
                and "apiResult" in responce["searchorderinfo_result"]:
            api_result = responce["searchorderinfo_result"]["apiResult"]
            if api_result["success"] is not True:
                error_msg = api_result["chineseErrCode"]
        if "searchorderinfo_result" in responce \
                and "orderInfoList" in responce["searchorderinfo_result"]:
            order_list = responce["searchorderinfo_result"]["orderInfoList"]
    return order_list, error_msg


def get_order_total(store_detail, start_stamp, end_stamp):
    res = get_order_response(store_detail, start_stamp, end_stamp, 1, 1)
    total_num = 0
    error_msg = None
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_pop_order_search_responce" in res:
        responce = res["jingdong_pop_order_search_responce"]
        if "searchorderinfo_result" in responce \
                and "apiResult" in responce["searchorderinfo_result"]:
            api_result = responce["searchorderinfo_result"]["apiResult"]
            if api_result["success"] is not True:
                error_msg = api_result["chineseErrCode"]
        if "searchorderinfo_result" in responce \
                and "orderTotal" in responce["searchorderinfo_result"]:
            total_num = responce["searchorderinfo_result"]["orderTotal"]
    return total_num, error_msg


# # order_state，多订单状态可以用英文逗号隔开
# # 1）WAIT_SELLER_STOCK_OUT 等待出库
# # 2）SEND_TO_DISTRIBUTION_CENER 发往配送中心（只适用于LBP，SOPL商家）
# # 3）DISTRIBUTION_CENTER_RECEIVED 配送中心已收货（只适用于LBP，SOPL商家）
# # 4）WAIT_GOODS_RECEIVE_CONFIRM 等待确认收货
# # 5）RECEIPTS_CONFIRM 收款确认（服务完成）（只适用于LBP，SOPL商家）
# # 6）WAIT_SELLER_DELIVERY 等待发货（只适用于海外购商家，等待境内发货 标签下的订单）
# # 7）FINISHED_L 完成
# # 8）TRADE_CANCELED 取消
# # 9）LOCKED 已锁定
# def get_order360_responce(
#         store_detail,
#         start_stamp,
#         end_stamp,
#         pageno,
#         pagesize):
#     if start_stamp < end_stamp - common_params.MONTH_1:
#         start_stamp = end_stamp - common_params.MONTH_1
#     now = time.time()
#     current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
#     end_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_stamp))
#     start_date = time.strftime(
#         "%Y-%m-%d %H:%M:%S",
#         time.localtime(start_stamp))
#     sys_params = {
#         "method": "360buy.order.search",
#         "access_token": store_detail["access_token"],
#         "app_key": store_detail["app_key"],
#         "timestamp": current_date,
#         "v": "2.0"
#     }
#     app_params = {
#         "start_date": start_date,
#         "end_date": end_date,
#         # "order_state": "4,5,6",
#         "order_state": "WAIT_GOODS_RECEIVE_CONFIRM,"
#                        "RECEIPTS_CONFIRM,WAIT_SELLER_DELIVERY",
#         "page": pageno,
#         "page_size": pagesize
#         # optional_fields 是否有默认值？
#     }
#
#     jos_api = JosAPI(
#         DOMAIN["api"],
#         sys_params,
#         app_params,
#         store_detail["app_secret"])
#     resp = jos_api.request()
#     if not resp:
#         return ""
#     res = json.loads(resp)
#     return res
#
#
# def get_order360_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
#     res = get_order360_responce(
#         store_detail,
#         start_stamp,
#         end_stamp,
#         pageno,
#         pagesize)
#     order_list = ""
#     error_msg = None
#     if "360buy_order_search_responce" in res \
#             and "orderSearchResponse" in res["360buy_order_search_responce"]:
#         responce = res["360buy_order_search_responce"]["orderSearchResponse"]
#         if "order_search" in responce and "order_info_list" in responce["order_search"]:
#             order_list = responce["order_search"]["order_info_list"]
#         if "codestr" in responce:
#             error_msg = responce["codestr"]
#     return order_list, error_msg
#
#
# def get_order360_total(store_detail, start_stamp, end_stamp):
#     res = get_order360_responce(store_detail, start_stamp, end_stamp, 1, 1)
#     total_num = 0
#     error_msg = None
#     if "360buy_order_search_responce" in res \
#             and "orderSearchResponse" in res["360buy_order_search_responce"]:
#         responce = res["360buy_order_search_responce"]["orderSearchResponse"]
#         if "order_search" in responce and "order_total" in responce["order_search"]:
#             total_num = responce["order_search"]["order_total"]
#         if "codestr" in responce:
#             error_msg = responce["codestr"]
#     return total_num, error_msg


def get_aftersale_response(store_detail, start_stamp, end_stamp, pageno, pagesize):
    if start_stamp < end_stamp - common_params.MONTH_1:
        start_stamp = end_stamp - common_params.MONTH_1
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    end_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_stamp))
    start_date = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    sys_params = {
        "method": "jingdong.ServiceInfoProvider.queryServicePage",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    app_params = {
        "buId": store_detail["store_key"],
        "pageIndex": pageno,
        "pageSize": pagesize,
        "afsApplyTimeBegin": start_date,
        "afsApplyTimeEnd": end_date
    }

    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return ""
    res = json.loads(resp)
    return res


def get_aftersale_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_aftersale_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize)
    order_list = ""
    error_msg = None
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_ServiceInfoProvider_queryServicePage_responce" in res:
        responce = res["jingdong_ServiceInfoProvider_queryServicePage_responce"]
        if "resultExport" in responce \
                and "data" in responce["resultExport"]:
            api_result = responce["resultExport"]["data"]
            order_list = api_result["serviceExportList"]
    return order_list, error_msg


def get_aftersale_total(store_detail, start_stamp, end_stamp):
    res = get_aftersale_response(store_detail, start_stamp, end_stamp, 1, 1)
    total_num = 0
    error_msg = None
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_ServiceInfoProvider_queryServicePage_responce" in res:
        responce = res["jingdong_ServiceInfoProvider_queryServicePage_responce"]
        if "resultExport" in responce \
                and "data" in responce["resultExport"]:
            api_result = responce["resultExport"]["data"]
            total_num = api_result["totalNum"]
    return total_num, error_msg


def get_aftersale_orders(
        user_param,
        store_detail,
        start_stamp,
        end_stamp,
        callback=None):
    total, error_msg = get_aftersale_total(store_detail, start_stamp, end_stamp)
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
        order_list, error_msg = get_aftersale_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        if isinstance(error_msg, str) and len(error_msg):
            return total, error_msg
        for order in order_list:
            order_detail, error_msg = get_order_detail(
                store_detail, order["orderId"])
            if order_detail is None:
                continue
            if isinstance(error_msg, str) and len(error_msg):
                return total, error_msg
            oms_order = transfer_order(
                order_detail, common_params.get_short_name(__file__), order)
            if oms_order is None:
                continue
            if callback:
                if index == 0:
                    status["callback_status"] = "start"
                else:
                    status["callback_status"] = "running"
                index += 1
                callback(user_param, store_detail, oms_order, index, status)
    if callback:
        status["callback_status"] = "end"
        status["end_stamp"] = time.time()
        callback(user_param, store_detail, None, index, status)
    return total, error_msg


def get_orders(
        user_param,
        store_detail,
        start_stamp,
        end_stamp,
        callback=None):
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
                store_detail, order["orderId"])
            if isinstance(error_msg, str) and len(error_msg):
                return total, error_msg
            oms_order = transfer_order(
                order_detail, common_params.get_short_name(__file__))
            if callback:
                if index == 0:
                    status["callback_status"] = "start"
                else:
                    status["callback_status"] = "running"
                index += 1
                callback(user_param, store_detail, oms_order, index, status)
    if callback:
        status["callback_status"] = "end"
        status["end_stamp"] = time.time()
        callback(user_param, store_detail, None, index, status)
    total, error_msg = get_aftersale_orders(user_param, store_detail, start_stamp, end_stamp, callback)
    return total, error_msg


# 订单转化
order_status_pair = {
    # 等待出库
    "WAIT_SELLER_STOCK_OUT": 20,

    # 等待发货（只适用于海外购商家，含义为'等待境内发货'标签下的订单,非海外购商家无需使用）
    "WAIT_SELLER_DELIVERY": 20,

    # 等待确认收货
    "WAIT_GOODS_RECEIVE_CONFIRM": 30,

    # 交易成功
    "FINISHED_L": 50,

    # 取消
    "TRADE_CANCELED": 60,
}

# 待审核 10001, 待客户反馈 10002, 审核不通过 10004, 待收货 10005, 待处理 10007, 待用户确认 10009, 完成 10010, 取消 10011
order_refund_status_pair = {
    # 售后处理中
    10001: 100,
    10002: 100,
    10005: 100,
    10007: 100,
    10009: 100,

    # 退款成功
    10010: 1,

    # 商家拒绝
    10004: -1,

    # 取消
    10011: -1
}


# # 京东订单转化
# def transfer_order(raw_order, prefix):
#     order = {}
#
#     order["order_id"] = str(uuid4())
#     order['order_code_oms'] = prefix + "_" + str(raw_order['orderId'])
#     order["order_code"] = raw_order["orderId"]  # 订单编号
#
#     # 支付方式（1货到付款, 2邮局汇款, 3自提, 4在线支付, 5公司转账, 6银行卡转账）
#     order["order_type"] = raw_order["payType"]
#     order["total_price"] = float(
#         raw_order["orderSellerPrice"])  # 订单货款金额（订单总金额-商家优惠金额）
#     order["goods_price"] = 0.0  # 商品单价
#     order["quantity"] = len(raw_order["itemInfoList"])  # 商品数量
#
#     order["express_number"] = raw_order["waybill"]  # 快递编号
#     order["express_fee"] = 0.0
#     if raw_order["freightPrice"]:
#         order["express_fee"] = float(raw_order["freightPrice"])      # 快递费
#     order["express_type"] = raw_order["logisticsId"]   # 快递公司编号
#     order["express_note"] = ""
#
#     order["express_type"] = ""
#
#     # 订单status：
#     order["status"] = 10
#     order["order_status_info"] = ""
#
#     order["status_ori"] = order_status_pair[raw_order["orderState"]]
#     order["refund_status_ori"] = 0
#
#     order["buyer_note"] = raw_order["orderRemark"]  # 买家留言
#     order["seller_note"] = raw_order["venderRemark"]  # 卖家备注
#
#     # 买家信息
#     order["consignee_name"] = raw_order["consigneeInfo"]["fullname"]        #
#     order["consignee_phone"] = raw_order["consigneeInfo"]["mobile"]  # 手机号码
#     # order["consignee_country"] = raw_order["consigneeInfo"]["country"]  # 国家
#     order["consignee_province"] = raw_order["consigneeInfo"]["province"]  # 省份
#     order["consignee_city"] = raw_order["consigneeInfo"]["city"]  # 城市
#     # 县 镇raw_order["consigneeInfo"]["town"]
#     order["consignee_area"] = raw_order["consigneeInfo"]["county"]
#     order["consignee_detail"] = raw_order["consigneeInfo"]["fullAddress"]  # 地址
#     #
#     order["pay_time"] = raw_order["paymentConfirmTime"]  # 付款时间
#     order["add_time"] = raw_order["orderStartTime"]  # 下单时间
#
#     # 转化订单详情
#     order_details = []
#     details = raw_order["itemInfoList"]
#     for detail in details:
#         order_detail = {}
#         order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
#         order_detail["sku_id"] = detail["outerSkuId"]  # str(uuid1())
#         order_detail["order_id"] = order["order_id"]  # 订单编号
#         # 产品明细编号
#         order_detail["item_code"] = detail["skuId"]
#         order_detail["price"] = 0.0
#         if detail["jdPrice"]:
#             order_detail["price"] = float(detail["jdPrice"])
#         order_detail["quantity"] = 0
#         if detail["itemTotal"]:
#             order_detail["quantity"] = int(detail["itemTotal"])
#         order_detail["total_price"] = order_detail["price"] * \
#             order_detail["quantity"]
#
#         order_detail["is_gift"] = False   # 是否赠品
#         order_detail["is_exist"] = True
#
#         order_details.append(order_detail)
#
#     order["order_details"] = order_details
#
#     # order_public = order_transfer_utils.get_public_info(
#     #     oms_order["platform_id"],
#     #     oms_order["store_id"],
#     #     oms_order["user_id"],
#     #     oms_order["store_is_auto_check"])
#     #
#     # for k in order_public:
#     #     order[k] = order_public[k]
#
#     return order


# 京东订单转化
def transfer_order(raw_order, prefix, raw_order_refund=None):
    order = {}

    order["order_id"] = str(uuid4())
    order['order_code_oms'] = prefix + "_" + str(raw_order['orderId'])
    order["order_code"] = raw_order["orderId"]  # 订单编号

    # 支付方式（1货到付款, 2邮局汇款, 3自提, 4在线支付, 5公司转账, 6银行卡转账）
    order["order_type"] = raw_order["payType"]
    order["total_price"] = float(
        raw_order["orderSellerPrice"])  # 订单货款金额（订单总金额-商家优惠金额）
    order["goods_price"] = 0.0  # 商品单价
    order["quantity"] = len(raw_order["itemInfoList"])  # 商品数量

    order["express_number"] = raw_order["waybill"]  # 快递编号
    order["express_fee"] = 0.0
    if raw_order["freightPrice"]:
        order["express_fee"] = float(raw_order["freightPrice"])      # 快递费
    order["express_type"] = raw_order["logisticsId"]   # 快递公司编号
    order["express_note"] = ""

    order["express_type"] = ""

    # 订单status：
    order["status"] = 10
    order["order_status_info"] = ""

    order["status_ori"] = order_status_pair[raw_order["orderState"]]
    order["refund_status_ori"] = 0
    if raw_order_refund:
        order["refund_status_ori"] = order_refund_status_pair[raw_order_refund["afsServiceStatus"]]
        if len(raw_order["itemInfoList"]) != 1:
            if order["refund_status_ori"] == 1:
                order["refund_status_ori"] = 2
    if order["refund_status_ori"] > 10:
        return None

    order["buyer_note"] = raw_order["orderRemark"]  # 买家留言
    order["seller_note"] = raw_order["venderRemark"]  # 卖家备注

    # 买家信息
    order["consignee_name"] = raw_order["consigneeInfo"]["fullname"]        #
    order["consignee_phone"] = raw_order["consigneeInfo"]["mobile"]  # 手机号码
    # order["consignee_country"] = raw_order["consigneeInfo"]["country"]  # 国家
    order["consignee_province"] = raw_order["consigneeInfo"]["province"]  # 省份
    order["consignee_city"] = raw_order["consigneeInfo"]["city"]  # 城市
    # 县 镇raw_order["consigneeInfo"]["town"]
    order["consignee_area"] = raw_order["consigneeInfo"]["county"]
    order["consignee_detail"] = raw_order["consigneeInfo"]["fullAddress"]  # 地址
    #
    order["pay_time"] = raw_order["paymentConfirmTime"]  # 付款时间
    order["add_time"] = raw_order["orderStartTime"]  # 下单时间

    # 转化订单详情
    order_details = []
    details = raw_order["itemInfoList"]
    for detail in details:
        valid = True
        if raw_order_refund:
            if detail["skuId"] != str(raw_order_refund["wareId"]):
                valid = False
        if valid:
            order_detail = {}
            order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
            order_detail["sku_id"] = detail["outerSkuId"]  # str(uuid1())
            order_detail["order_id"] = order["order_id"]  # 订单编号
            # 产品明细编号
            order_detail["item_code"] = detail["skuId"]
            order_detail["price"] = 0.0
            if detail["jdPrice"]:
                order_detail["price"] = float(detail["jdPrice"])
            order_detail["quantity"] = 0
            if detail["itemTotal"]:
                order_detail["quantity"] = int(detail["itemTotal"])
            order_detail["total_price"] = order_detail["price"] * \
                order_detail["quantity"]

            order_detail["is_gift"] = False   # 是否赠品
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


def get_sku_list(store_detail, ware_id, pageno, pagesize):
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    sys_params = {
        "method": "jingdong.sku.read.searchSkuList",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    app_params = {
        "wareId": ware_id,
        "page": pageno,
        "page_size": pagesize,
        "field": "skuName,barCode,wareTitle,categoryId,stockNum,modified,saleAttrs,features"
    }
    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return None, None
    sku_list = None
    error_msg = None
    res = json.loads(resp)
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_sku_read_searchSkuList_responce" in res \
            and "page" in res["jingdong_sku_read_searchSkuList_responce"]:
        page = res["jingdong_sku_read_searchSkuList_responce"]["page"]
        if "data" in page:
            sku_list = page["data"]

    return sku_list, error_msg


def get_ware_reponse(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize):
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    sys_params = {
        "method": "jingdong.ware.read.searchWare4Valid",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    # 商品状态, 多个值属于[或]
    # 操作
    # 1: 从未上架
    # 2: 自主下架
    # 4: 系统下架
    # 8: 上架
    # 513: 从未上架待审
    # 514: 自主下架待审
    # 516: 系统下架待审
    # 520: 上架待审核
    # 1028: 系统下架审核失败
    app_params = {
        "wareStatusValue": "8,520",
        "pageNo": pageno,
    }
    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return ""
    res = json.loads(resp)
    return res


def get_ware_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_ware_reponse(store_detail, start_stamp, end_stamp, pageno, pagesize)
    ware_list = ""
    error_msg = None
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_ware_read_searchWare4Valid_responce" in res \
            and "page" in res["jingdong_ware_read_searchWare4Valid_responce"]:
        page = res["jingdong_ware_read_searchWare4Valid_responce"]["page"]
        if "data" in page:
            ware_list = page["data"]

    return ware_list, error_msg


# inside：内部使用标识
def get_ware_total(store_detail, start_stamp, end_stamp, inside=False):
    res = get_ware_reponse(store_detail, start_stamp, end_stamp, 10000, 1)
    error_msg = None
    total_num = 0
    pagesize = 0
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    if "jingdong_ware_read_searchWare4Valid_responce" in res \
            and "page" in res["jingdong_ware_read_searchWare4Valid_responce"]:
        page = res["jingdong_ware_read_searchWare4Valid_responce"]["page"]
        if "totalItem" in page:
            total_num = page["totalItem"]
        if "pageSize" in page:
            pagesize = page["pageSize"]
    if inside is True:
        return total_num, pagesize, error_msg
    return total_num, error_msg


def get_wares(user_param, store_detail,
              start_stamp, end_stamp, callback=None):
    total, pagesize, error_msg = get_ware_total(store_detail, start_stamp, end_stamp, True)
    if total <= 0:
        return total, error_msg
    # print("商品总数为: ", total)
    if pagesize == 0:
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
            skus, error_msg = get_sku_list(store_detail, ware["wareId"],
                                           1, common_params.PAGE_SIZE)
            if isinstance(error_msg, str) and len(error_msg):
                return total, error_msg
            sku_list = to_oms_sku(
                store_detail["user_id"], skus)
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
    for item in ware:
        sku = {
            "user_id": str(user_id),
            "item_code": str(item["skuId"]),
            "outer_item_code": item["outerId"],
            "sku_name": str(item["skuName"]),
            "specification": "",
            "bar_code": "",
            # "user_code": "",
            "price": float(item["jdPrice"]),
            "unit": "",
            "goods_no": item["wareId"],
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


class JosAPI:
    def __init__(self, api, method, param, appsecret):
        self.app_secret = appsecret
        self.api = api
        self.request_params = method
        self.request_params['360buy_param_json'] = json.dumps(
            param, ensure_ascii=False)

    # 生成签名和请求的url
    def make_sign(self):
        keys = sorted(self.request_params.keys())
        md5_str = self.app_secret
        api_url = ""
        for key in keys:
            md5_str += key
            md5_str += self.request_params[key]
            if api_url:
                api_url += ('&' + key + '=' + self.request_params[key])
            else:
                api_url += (key + '=' + self.request_params[key])
        md5_str += self.app_secret

        sign_hash = md5()
        sign_hash.update(md5_str.encode())
        sign = sign_hash.hexdigest()
        self.request_params['sign'] = sign.upper()

        url = self.api + api_url + '&sign=' + sign.upper()
        return url

    # 发送请求
    def request(self):
        request_url = self.make_sign()
        print(request_url)
        response = requests_util.post(request_url)
        if response is None:
            return response
        return response.text


# 获取商家物流公司
def get_express_list(store_detail):
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    sys_params = {
        "method": "360buy.get.vender.all.delivery.company",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    app_params = {
        "fields": "id,name,description"
    }
    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return ""
    res = json.loads(resp)

    express_list = {}
    error_msg = None
    if "vender_delivery_all_company_response" in res:
        response = res["vender_delivery_all_company_response"]
        if "delivery_companies" in response:
            express_list = response["delivery_companies"]
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]

    return express_list, error_msg


# 订单发货处理 express_code：快递公司代码；deliver_no：快递单号；item_details 部分发货参数，不填为整单发货
def order_delivery(store_detail, order_id, express_code, deliver_no, item_details=None):
    express = transfer_express.get(express_code)
    if express is None:
        return False, "express_code is not found"
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    sys_params = {
        "method": "360buy.order.sop.outstorage",
        "access_token": store_detail["access_token"],
        "app_key": store_detail["app_key"],
        "timestamp": current_date,
        "v": "2.0"
    }
    app_params = {
        "logistics_id": express["id"],
        "waybill": deliver_no,
        "order_id": order_id,
    }
    jos_api = JosAPI(
        DOMAIN["api"],
        sys_params,
        app_params,
        store_detail["app_secret"])
    resp = jos_api.request()
    if not resp:
        return ""
    res = json.loads(resp)
    success = False
    error_msg = None
    # TODO
    # 正常发货未测试
    if "vender_delivery_all_company_response" in res:
        response = res["vender_delivery_all_company_response"]
        if "delivery_companies" in response:
            express_list = response["delivery_companies"]
    if "error_response" in res:
        if res["error_response"]["code"]:
            error_msg = res["error_response"]["zh_desc"]
    return success, error_msg


# # 检索商家物流公司信息，只可获取商家后台已设置的物流公司信息
# def get_express_list_1(store_detail):
#     now = time.time()
#     current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
#     sys_params = {
#         "method": "360buy.delivery.logistics.get",
#         "access_token": store_detail["access_token"],
#         "app_key": store_detail["app_key"],
#         "timestamp": current_date,
#         "v": "2.0"
#     }
#     app_params = {
#     }
#     jos_api = JosAPI(
#         DOMAIN["api"],
#         sys_params,
#         app_params,
#         store_detail["app_secret"])
#     resp = jos_api.request()
#     if not resp:
#         return ""
#     res = json.loads(resp)
#
#     express_list = {}
#     error_msg = None
#     if "delivery_logistics_get_response" in res \
#             and "logistics_companies" in res["delivery_logistics_get_response"]:
#         logistics_list = res["delivery_logistics_get_response"]["logistics_companies"]
#         if "logistics_list" in logistics_list:
#             express_list = logistics_list["logistics_list"]
#     if "error_response" in res:
#         if res["error_response"]["code"]:
#             error_msg = res["error_response"]["zh_desc"]
#
#     return express_list, error_msg


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
        'id': 467,
        'express_company': '顺丰快递'
    },
    # 标准快递
    'EMS': {
        'id': 465,
        'express_company': '邮政EMS'
    },
    #
    'EYB': None,
    # 宅急送
    'ZJS': {
        'id': 1409,
        'express_company': '宅急送'
    },
    # 圆通
    'YTO': {
        'id': 463,
        'express_company': '圆通快递'
    },
    # 中通(ZTO)
    'ZTO': {
        'id': 1499,
        'express_company': '中通速递'
    },
    # 百世汇通
    'HTKY': None,
    # 优速
    'UC': {
        'id': 1747,
        'express_company': '优速快递'
    },
    #
    'STO': {
        'id': 470,
        'express_company': '申通快递'
    },
    # 天天快递
    'TTKDEX': None,
    # 全峰
    'QFKD': {
        'id': 2016,
        'express_company': '全峰快递'
    },
    # 快捷
    'FAST': {
        'id': 2094,
        'express_company': '快捷速递'
    },
    # 邮政小包
    'POSTB': {
        'id': 2170,
        'express_company': '邮政快递包裹'
    },
    # 国通
    'GTO': {
        'id': 2465,
        'express_company': '国通快递'
    },
    # 韵达
    'YUNDA': {
        'id': 1327,
        'express_company': '韵达快递'
    },
    # 京东配送
    'JD': {
        'id': 336878,
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
store_detail = {
    "platform_id": 2,
    "platform_name": "jingdong",
    "store_key": "691764",
    "app_key": "8D311921DE6B681D671AC7F3C52B96D6",
    "app_secret": "85d0c2caf3c449d08751b44ef7316df1",
    "access_token": "b62953c7-d618-4d4d-990b-e1b8b58c5c7b",
    "refresh_token": "d1aae42b-b0ea-4697-85f5-c1523afa1cd6",
    "id": "st1000000110001",
    "user_id": 10000001,
    "last_get_order_at": "2017-11-2 16:00:00",
    "store_is_auto_check": True,
}
# get_express_list(store_detail)
#
# refresh_token(store_detail, common_params.TIMEOUT)
#
# store_id = "1ab3334d-d57f-4dcb-9c7c-68d3afdcc88d"
# start_time = "2017-10-26 0:0:0"
# # end_time = "2017-9-11 0:0:0"
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# # end_stamp = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()
#
# # 测试获取订单
# get_orders(store_id, store_detail, start_stamp, end_stamp, order_detail_callback)
#
# # 测试获取商品信息
# get_wares(store_id, store_detail, start_stamp, end_stamp, ware_detail_callback)
