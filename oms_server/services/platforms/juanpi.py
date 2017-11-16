#!/usr/bin/python3
#  -*- coding: utf-8 -*-

# 卷皮接口
import time
import json
import urllib.parse
from uuid import uuid4
from oms_server.services.platforms import requests_util
from oms_server.services.platforms import common_params


DOMAIN = {
    # 沙箱环境
    "api": "http://61.183.199.130:2016/erpapi/index",
    # 正式环境
    # "api": "http://open.juanpi.com/erpapi/index",
    "get_express": "http://open.juanpi.com/erpapi/get_express",

    "oauth": "http://61.183.199.130:2016/erpapi/authorize/erpapi/index?"
}

# static $deal_status_text = [
#         //买家申请退款，等待卖家处理
#         60=>['买家申请退款，等待卖家处理'],
#         62=>['买家申请退款，等待卖家处理'],
#         64=>['买家申请退款，等待卖家处理'],
#         80=>['买家申请退款，等待卖家处理'],
#         //卖家审核通过，等待买家寄回
#         82=>['卖家审核通过，等待买家寄回'],
#         84=>['卖家审核通过，等待买家寄回'],
#         //卖家审核不通过
#         83=>['卖家审核不通过'],
#         98=>['卖家审核不通过'],
#         95=>['卖家审核不通过'],
#         //买家已寄回，等待卖家确认收货
#         85=>['买家已寄回，等待卖家确认收货'],
#         99=>['买家已寄回，等待卖家确认收货'],
#         //卖家同意退款
#         65=>['卖家同意退款，等待退款到账','退款成功'],
#         69=>['卖家同意退款，等待退款到账','退款成功'],
#         90=>['卖家同意退款，等待退款到账','退款成功'],
#         91=>['卖家同意退款，等待退款到账','退款成功'],
#         68=>['卖家同意退款，等待退款到账','退款成功'],
#         89=>['卖家同意退款，等待退款到账','退款成功'],
#         //卖家拒绝退款
#         70=>['卖家拒绝退款'],
#         86=>['卖家拒绝退款'],
#         92=>['卖家拒绝退款'],
#         100=>['卖家拒绝退款'],
#         66=>['卖家拒绝退款'],
#         87=>['卖家拒绝退款'],
#         //售后关闭
#         71=>['售后关闭'],
#         93=>['售后关闭'],
#         67=>['售后关闭'],
#         88=>['售后关闭'],
#         97=>['售后关闭'],
#         //售后撤销
#         61=>['售后撤销'],
#         81=>['售后撤销'],
#     ];


def refresh_token(store_detail, timeout=common_params.TIMEOUT):
    url = DOMAIN.get("oauth", "")
    data = {
        "secret": store_detail["app_key"],
        "scope": "order_list,order_info,sgoods_list,sgoods_info,send_goods,aftersale_list,aftersale_detail"
    }
    resp = requests_util.post(url, data=data, timeout=timeout)
    res = json.loads(resp.text)
    access_token = None
    if "data" in res and "token" in res["data"]:
        access_token = res["data"]["token"]
        store_detail['expire_in'] = res["data"]['expire']
        store_detail['access_token'] = res["data"]['token']
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    return access_token, error_msg


# 获取商品详情&sku列表
def get_ware_detail(store_detail, ware_id):
    # url = "https://open.youzan.com/api/oauthentry/youzan.item/3.0.0/get"
    url = DOMAIN["api"]
    app_params = {
        "jType": "sgoods_info",
        "jCusKey": store_detail["store_key"],
        "jSgoodsId": ware_id,
        "type": "json",
        "token": store_detail["access_token"],
        "field": "skuid,zid,fid,zid_value,fid_value,price,cprice,inventory,sales,sgoodsno,add_time,last_modified"}
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)

    error_msg = None
    if "error_response" in res:
        if "msg" in res["error_response"]:
            error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]

    ware_detail = {}
    if "data" not in res:
        return "", error_msg
    if "sgoodsinfo" not in res["data"]:
        return "", error_msg
    ware_detail.update(res["data"]["sgoodsinfo"])
    if "list" not in res["data"]:
        return "", error_msg
    ware_detail_list = res["data"]["list"]
    if len(ware_detail_list) > 0:
        ware_detail["list"] = (ware_detail_list)
    return ware_detail, error_msg


def get_ware_reponse(
    store_detail,
    start_stamp,
    end_stamp,
    pageno,
    pagesize,
):
    onsale_time = str(int(start_stamp)) + "|" + str(int(end_stamp))
    url = DOMAIN["api"]
    app_params = {
        "jType": "sgoods_list",
        "jCusKey": store_detail["store_key"],
        "jPagesize": pagesize,
        "jPage": pageno,
        "type": "json",
        "token": store_detail["access_token"],
        "field": "sgoodsid,sgoodsid_v2,cgid,title,cname",
        "onsale_time": onsale_time
    }
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return ""
    res = json.loads(resp.text)
    return res


# 获取商品列表
def get_ware_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_ware_reponse(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    if "data" not in res:
        return "", error_msg
    if "list" not in res["data"]:
        return "", error_msg
    ware_list = res["data"]["list"]
    return ware_list, error_msg


def get_ware_total(store_detail, start_stamp, end_stamp):
    res = get_ware_reponse(store_detail, start_stamp, end_stamp, 1, 1)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    total_num = 0
    if "data" not in res:
        return 0, error_msg
    if "count" not in res["data"]:
        return 0, error_msg
    if len(res["data"]["count"]):
        total_num = int(res["data"]["count"])
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
            ware_detail, error_msg = get_ware_detail(
                store_detail, ware["sgoodsid"])
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


# 同一个商品ID下可以有多个sku
def to_oms_sku(user_id, ware):
    skus = []
    if not ware:
        return skus
    for item in ware['list']:
        # quantity = 0
        # if item['inventory']:
        #     quantity = int(item['inventory'])
        sku = {
            "user_id": str(user_id),
            "item_code": str(item['skuid']),
            "outer_item_code": "",
            "sku_name": str(ware['title'])+item["zid_value"]+item["fid_value"],
            "specification": "",
            "bar_code": "",
            # "user_code": "",
            "price": float(item["price"]) - float(item["cprice"]),
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
        skus.append(sku)
    return skus


def make_md5(params, code):
    from hashlib import md5
    base_param_list = sorted(params.items(), key=lambda d: d[0], reverse=False)

    param_list = base_param_list[:]
    code_list = sorted(code.items(), key=lambda d: d[0], reverse=False)
    for item in code_list:
        param_list.append(item)

    param_str = urllib.parse.urlencode(param_list)

    md51 = md5()
    md51.update(param_str.encode())
    param_md5 = md51.hexdigest()
    # print(param_md5)
    # sign = {"sign": param_md5}
    data = params.copy()
    data["sign"] = param_md5
    return data


# 获取订单详细
def get_order_detail(store_detail, order_id):
    url = DOMAIN["api"]
    app_params = {
        "jType": "order_info",
        "jCusKey": store_detail["store_key"],
        "type": "json",
        "token": store_detail["access_token"],
        "jOrderNo": order_id
    }
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    order_detail = ""
    if "data" in res:
        order_detail = res["data"]
    return order_detail, error_msg


# 订单状态: 1:等待买家付款,2:等待发货,3:已发货,5:交易成功,6:交易已关闭,9:备货中, 默认值为1 多个用,隔开
def get_order_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize,
        order_status=2):
    update_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_stamp))
    update_start = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    create_time = str(int(start_stamp)) + "|" + str(int(end_stamp))
    url = DOMAIN["api"]
    app_params = {
        "jType": "order_list",
        "jCusKey": store_detail["store_key"],
        "jPagesize": pagesize,
        "jPage": pageno,
        "type": "json",
        "token": store_detail["access_token"],
        "jOrderStatus": order_status,
        "create_time": create_time,
        # "show_detail": 1
    }
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return ""
    res = json.loads(resp.text)
    return res


# 获取订单列表
def get_order_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_order_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    order_list = ""
    if "data" in res and "lists" in res["data"]:
        order_list = res["data"]["lists"]
    return order_list, error_msg


def get_order_total(store_detail, start_stamp, end_stamp):
    res = get_order_response(store_detail, start_stamp, end_stamp, 1, 1)
    if res["info"].isdigit():
        error_msg = JuanpiErrorCodes[res["info"]]
    else:
        error_msg = res["info"]
    order_total = 0
    if "data" in res and "count" in res["data"]:
        order_total = int(res["data"]["count"])
    return order_total, error_msg


def get_orders(
        user_param, store_detail,
        start_stamp, end_stamp, callback=None):
    total, error_msg = get_order_total(store_detail, start_stamp, end_stamp)
    if total <= 0:
        return total, error_msg
    pagesize = common_params.PAGE_SIZE
    # print("订单总数为: ", total)
    pages = common_params.get_pages(total, pagesize)
    index = 0
    status = {}
    for i in range(pages):
        pageno = i + 1
        order_list, error_msg = get_order_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        if isinstance(error_msg, str) and len(error_msg):
            return total, error_msg
        for order in order_list:
            order_detail, error_msg = get_order_detail(
                store_detail, order["orderno"])
            if isinstance(error_msg, str) and len(error_msg):
                return total, error_msg
            oms_order = transfer_order(order_detail, common_params.get_short_name(__file__))
            if callback:
                if index == 0:
                    status["callback_status"] = "start"
                    status["start_stamp"] = time.time()
                index += 1
                callback(user_param, store_detail, oms_order, index, status)
        if callback:
            status["callback_status"] = "end"
            status["end_stamp"] = time.time()
            callback(user_param, store_detail, None, index, status)
        return total, error_msg


# 获取售后详细
def get_aftersale_detail(store_detail, backno):
    url = DOMAIN["api"]
    app_params = {
        "jType": "aftersale_detail",
        "jCusKey": store_detail["store_key"],
        "type": "json",
        "token": store_detail["access_token"],
        "boNo": backno
    }
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    order_detail = ""
    if "data" in res:
        order_detail = res["data"]
    return order_detail, error_msg


# 订单状态: 1:等待买家付款,2:等待发货,3:已发货,5:交易成功,6:交易已关闭,9:备货中, 默认值为1 多个用,隔开
def get_aftersale_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize,
        aftersale_type=2):
    if start_stamp < end_stamp - common_params.DAY_1 * 7:
        start_stamp = end_stamp - common_params.DAY_1 * 7
    modefied_time = str(int(start_stamp)) + "|" + str(int(end_stamp))
    url = DOMAIN["api"]
    app_params = {
        "jType": "aftersale_list",
        "jCusKey": store_detail["store_key"],
        "jPagesize": pagesize,
        "jPage": pageno,
        "type": "json",
        "token": store_detail["access_token"],
        "aftersaleType": aftersale_type,        # 售后类型: 1 仅退款; 2 退货退款
        "modefied_time": modefied_time,
        # "show_detail": 1
    }
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return ""
    res = json.loads(resp.text)
    return res


# 获取订单列表
def get_aftersale_list(store_detail, start_stamp, end_stamp, pageno, pagesize):
    res = get_aftersale_response(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    order_list = ""
    if "data" in res and "list" in res["data"]:
        order_list = res["data"]["list"]
    return order_list, error_msg


def get_aftersale_total(store_detail, start_stamp, end_stamp):
    res = get_aftersale_response(store_detail, start_stamp, end_stamp, 1, 10)
    if res["info"].isdigit():
        error_msg = JuanpiErrorCodes[res["info"]]
    else:
        error_msg = res["info"]
    order_total = 0
    if "data" in res and "total" in res["data"]:
        order_total = int(res["data"]["total"])
    return order_total, error_msg


def get_aftersale_orders(
        store_id,
        store_detail,
        start_stamp,
        end_stamp,
        callback=None):
    total, error_msg = get_aftersale_total(
        store_detail, start_stamp, end_stamp)
    if total <= 0:
        return total, error_msg
    pagesize = common_params.PAGE_SIZE
    print("订单总数为: ", total)
    pages = common_params.get_pages(total, pagesize)
    for i in range(pages):
        pageno = i + 1
        order_list, error_msg = get_aftersale_list(
            store_detail, start_stamp, end_stamp, pageno, pagesize)
        for order in order_list:
            aftersale_order_detail, error_msg = get_aftersale_detail(
                store_detail, order["backno"])
            if callback:
                callback(
                    store_id,
                    store_detail,
                    transfer_aftersale_order(
                        aftersale_order_detail,
                        common_params.get_short_name(__file__)))


# 卷皮订单转化
order_status_pair = {
    # 等待买家付款
    "1": 10,

    # 等待发货
    "2": 20,

    # 已发货
    "3": 30,
    # 备货中(包括备货中和部分发货订
    "9": 31,
    # 部分发货(同备货中，即将废除)
    "10": 31,

    # 交易成功
    "5": 50,

    # 交易已关闭
    "6": 60,
}


# 卷皮退款转化
order_refund_status_pair = {
    # 买家申请退款，等待卖家处理
    "60": 1,
    "62": 1,
    "64": 1,
    "80": 1,

    # 卖家审核不通过
    "83": 1,
    "98": 1,
    "95": 1,

    # 卖家拒绝退款
    "70": 1,
    "86": 1,
    "92": 1,
    "100": 1,
    "66": 1,
    "87": 1,

    # '卖家同意退款，等待退款到账','退款成功'
    "65": 2,
    "69": 2,
    "90": 2,
    "91": 2,
    "68": 2,
    "89": 2,

    # 售后关闭
    "71": 3,
    "93": 3,
    "67": 3,
    "88": 3,
    "97": 3,

    # 售后撤销
    "61": 4,
    "81": 4,
}

JuanpiErrorCodes = {
    "10001": "参数丢失",
    "10002": "非法请求，不在的接口",
    "10003": "不存在的SECRET或SECRET不可用",
    "10004": "TOKEN无效，过期或者不存在",
    "10005": "ERP权限不正确",
    "10006": "ERP帐号被禁用",
    "10007": "没有查询到数据",
    "10008": "不存在的订单",
    "10009": "订单状态不在待发货或备货中",
    "10010": "ERP帐号异常",
    "10011": "商家状态不可用",
    "10012": "不存在此商家",
    "10013": "商家密钥错误",
    "10014": "商家密钥过期",
    "10015": "订单已发货",
    "10016": "订单商品全部售后中",
    "10017": "发货号和快递公司不匹配",
    "10018": "订单类型不能发货",
    "10019": "库存设置保护时间(5分钟)",
    "10020": "修改后库存需大于销量+50",
    "10021": "服务化库存查询错误",
    "10022": "服务化库存设置错误",
    "10023": "入库商品不能修改库存",
    "10024": "用户与商品所属商家不一致",
    "10025": "商品未上架, 不可修改库存",
    "10026": "入库商品不可查询",
    "10027": "物流公司不存在",
    "10028": "商品数据错误, 无法同步库存",
    "10029": "订单类型不支持查询",
    "10030": "等待上架商品sku修改后总库存不能低于10",
    "10031": "上架商品sku修改后库存必须大于销量+50",
    "10032": "不支持该订单状态修改收货地址",
    "10033": "改商品不能被erp同步库存",
    "10034": "发货失败（当前订单不在可发货状态）",
    "10035": "发货失败（物流单号已被使用）",
    "10036": "发货失败（物流单号已有物流信息)",
    "10037": "试用商品，不支持库存设置",
    "10038": "发货商品中存在仓储商品，不可以发货",
    "10040": "TOKEN失效",
    "10041": "签名错误",
    "10042": "TOKEN权限不足",
    "20000": None,  # 操作成功
    "50000": "服务器错误，如redis写入失败",
    "50002": "scope为空",
    "50003": "Ip 访问频率过高受限",
    "50004": "单个用户访问频率受限"
}


# 卷皮订单转化
def transfer_order(raw_order, prefix):
    order = {}

    order["order_id"] = str(uuid4())
    order["order_code_oms"] = prefix + "_" + str(raw_order["orderno"])

    # 支付方式 1：卷皮充值 2：支付宝 3：银联 4：财 付通 5：支付宝手机版 6：支付宝 pc7：客户端微 信 8：wap 微信 9：pc 微信
    order["order_type"] = raw_order["paytype"]
    order["order_code"] = raw_order["orderno"]  # 交易编号
    order["total_price"] = raw_order["realmoney"]  # 总价格
    order["goods_price"] = raw_order["goodslist"][0]["goodsprice"]  # 商品单价
    order["quantity"] = raw_order["goodslist"][0]["goodsnum"]  # 商品数量

    order["express_number"] = raw_order["expresscode"]
    order["express_fee"] = float(raw_order["payexpress"])
    order["express_type"] = ""
    order["express_note"] = ""

    # 物流方式 取值范围：express（快递），fetch（到店自提），local（同城配送）
    # order["express_type"] = raw_order["shipping_type"]

    order["status"] = 10
    order["order_status_info"] = ""

    order["status_ori"] = order_status_pair[str(
        raw_order["status"])]  # 订单状态 枚举值
    order["refund_status_ori"] = 0  # 退款状态'''

    order["buyer_note"] = raw_order["remark"]  # 买家留言
    order["seller_note"] = raw_order["sellremark"]  # 卖家备注

    # 买家信息
    order["consignee_name"] = raw_order["buyername"]        #
    order["consignee_phone"] = raw_order["buyerphone"]  # 电话
    order["consignee_province"] = raw_order["buyerarea"]  # 省份
    order["consignee_city"] = ""  # 城市
    order["consignee_area"] = ""  # 地区
    order["consignee_detail"] = raw_order["buyeraddress"]  # 地址

    order["pay_time"] = raw_order["paytime"]  # 支付时间
    order["add_time"] = raw_order["createtime"]  # "下单时间

    # 转化订单详情
    order_details = []
    details = raw_order["goodslist"]
    for detail in details:
        order_detail = {}
        order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
        order_detail["sku_id"] = detail["goods_sku_id"]  # str(uuid1())
        order_detail["order_id"] = order["order_id"]  # 订单编号
        order_detail["item_code"] = detail["itemid"]  # 交易明细编号
        order_detail["price"] = float(detail["goodsprice"])
        order_detail["quantity"] = int(detail["goodsnum"])
        order_detail["total_price"] = order_detail["quantity"] * \
            order_detail["price"]

        order_detail["is_gift"] = detail["isgift"]
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


# 卷皮订单转化
def transfer_aftersale_order(raw_order, prefix):
    order = {}

    order["order_id"] = str(uuid4())
    order["order_code_oms"] = prefix + str(raw_order["orderno"])

    # 支付方式 1：卷皮充值 2：支付宝 3：银联 4：财 付通 5：支付宝手机版 6：支付宝 pc7：客户端微 信 8：wap 微信 9：pc 微信
    order["order_type"] = ""    # raw_order["paytype"]
    order["order_code"] = raw_order["orderno"]  # 交易编号
    order["total_price"] = raw_order["money"]  # 申请金额
    order["goods_price"] = float(raw_order["goodsprice"])  # 商品单价
    order["quantity"] = raw_order["goods_nums"]  # 商品数量

    order["express_number"] = ""
    order["express_fee"] = 0
    order["express_type"] = ""
    order["express_note"] = ""

    # 物流方式 取值范围：express（快递），fetch（到店自提），local（同城配送）
    # order["express_type"] = raw_order["shipping_type"]

    order["order_status_info"] = ""

    order["status_ori"] = ""
    order["refund_status_ori"] = order_refund_status_pair.get(str(
        raw_order["dealstatus"]), 0)  # 订单状态 枚举值

    order["buyer_note"] = raw_order["refundnote"]  # 申请说明
    order["seller_note"] = ""  # 卖家备注

    # 买家信息
    order["consignee_name"] = ""        #
    order["consignee_phone"] = ""  # 电话
    order["consignee_province"] = ""  # 省份
    order["consignee_city"] = ""  # 城市
    order["consignee_area"] = ""  # 地区
    order["consignee_detail"] = ""  # 地址

    order["pay_time"] = ""  # 支付时间
    order["add_time"] = ""  # 下单时间

    # 转化订单详情
    order_details = []
    order_detail = {}
    order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
    order_detail["sku_id"] = raw_order["skuid"]  # str(uuid1())
    order_detail["order_id"] = order["order_id"]  # 订单编号
    order_detail["item_code"] = ""  # 交易明细编号
    order_detail["price"] = float(raw_order["goodsprice"])
    order_detail["quantity"] = int(raw_order["goods_nums"])
    order_detail["total_price"] = order_detail["quantity"] * \
        order_detail["price"]

    order_detail["is_gift"] = False
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


# 获取快递信息
def get_express_list():
    url = DOMAIN["get_express"]
    resp = requests_util.post(url=url)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    express_list = {}
    if "info" in res and res["info"] == "20000":
        express_info = res["data"]
        for item in express_info:
            express = express_info[item]
            express_list[express["companyname"]] = express
    return express_list, error_msg


# 订单发货处理 express_code：快递公司代码；deliver_no：快递单号；
def order_delivery(store_detail, order_id, express_code, deliver_no, item_details=None):
    express = transfer_express.get(express_code)
    if express is None:
        return False, "express_code is not found"
    url = DOMAIN["api"]
    app_params = {
        "jType": "send_goods",
        "jCusKey": store_detail["store_key"],
        "jOrderNo": order_id,
        "jDeliverEname": express["companypinyin"],
        "jDeliverCname": express["companyname"],
        "jDeliverNo": deliver_no,
        "type": "json",
        "token": store_detail["access_token"],
    }
    if item_details:
        if "jOrderGiftIds" in item_details and "jOrderGoodsIds" in item_details:
            app_params["jOrderGiftIds"] = item_details["jOrderGiftIds"]
            app_params["jOrderGoodsIds"] = item_details["jOrderGoodsIds"]
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return False, common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    success = False
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    if "info" in res and res["info"] == "20000":
        success = True
    return success, error_msg


def order_delivery_split(
        store_detail,
        order_id,
        express_code,
        deliver_no,
        skus_param):
    if express_code is None:
        return False, "express_code is None"
    url = DOMAIN["api"]
    app_params = {
        "jType": "send_goods",
        "jCusKey": store_detail["store_key"],
        "jOrderNo": order_id,
        "jDeliverEname": express_code["companypinyin"],
        "jDeliverCname": express_code["companyname"],
        "jDeliverNo": deliver_no,
        "type": "json",
        "token": store_detail["access_token"],
        "jIsSplit": 1,
        "jOrderGiftIds": skus_param["jOrderGiftIds"],
        "jOrderGoodsIds": skus_param["jOrderGoodsIds"]
    }
    code = {
        "code": store_detail["app_secret"]
    }
    data = make_md5(app_params, code)

    resp = requests_util.post(url=url, data=data)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    success = False
    error_msg = None
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = JuanpiErrorCodes[res["info"]]
        else:
            error_msg = res["info"]
    if "info" in res and res["info"] == "20000":
        success = True
    return success, error_msg


transfer_express = {
    # 顺丰
    'SF': {
        'companyname': '顺丰速运',
        'companypinyin': 'shunfeng',
    },
    # 标准快递
    'EMS': {
        'companyname': 'EMS标准快递',
        'companypinyin': 'emsbiaozhun',
    },
    #
    'EYB': {
        'companyname': 'EMS经济快递',
        'companypinyin': 'ems',
    },
    # 宅急送
    'ZJS': {
        'companyname': '宅急送',
        'companypinyin': 'zhaijisong',
    },
    # 圆通
    'YTO': {
        'companyname': '圆通速递',
        'companypinyin': 'yuantong',
    },
    # 中通(ZTO)
    'ZTO': {
        'companyname': '中通快运',
        'companypinyin': 'zhongtongkuaiyun',
    },
    # 百世汇通
    'HTKY': {
        'companyname': '百世物流',
        'companypinyin': 'baishiwuliu',
    },
    # 优速
    'UC': {
        'companyname': '优速物流',
        'companypinyin': 'youshuwuliu',
    },
    #
    'STO': {
        'companyname': '申通快递',
        'companypinyin': 'shentong',
    },
    # 天天快递
    'TTKDEX': {
        'companyname': '天天快递',
        'companypinyin': 'tiantian',
    },
    # 全峰
    'QFKD': {
        'companyname': '全峰快递',
        'companypinyin': 'quanfengkuaidi',
    },
    # 快捷
    'FAST': {
        'companyname': '快捷快递',
        'companypinyin': 'kuaijiesudi',
    },
    # 邮政小包
    'POSTB': {
        'companyname': '邮政快递包裹',
        'companypinyin': 'youzhengguonei',
    },
    # 国通
    'GTO': {
        'companyname': '国通快递',
        'companypinyin': 'guotongkuaidi',
    },
    # 韵达
    'YUNDA': {
        'companyname': '韵达快递',
        'companypinyin': 'yunda',
    },
    # 京东配送
    'JD': {
        'companyname': '京东物流',
        'companypinyin': 'jingdongwuliu',
    },
    # 当当宅配
    'DD': None,
    # 亚马逊物流
    'AMAZON': None,
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
#     "app_key": "ab6a26b46d1ee168876f9cebedc8f0d6",
#     "app_secret": "72d84b2d8ff9a9cbd9533eab0d32d53e",
#     "access_token": "8255d6299db1e64e6796d7a8720199c1f8c2e975",
#     "store_key": "48A29615B1F9A58A5E85",
#     # "store_key": "CA3235EA5591E03E72D7",
#     "platform_name": "juanpi",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }
#
# refresh_token(store_detail)
# store_detail["access_token"] = get_token(store_detail)
# store_id = "1ab3334d-d57f-4dcb-9c7c-68d3afdcc88d"
#
# start_time = "2017-9-22 0:0:0"
# end_time = "2017-9-28 0:0:0"
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()
#
# # 获取订单
# total, error_msg = get_orders(store_id, store_detail, start_stamp, end_stamp, order_detail_callback)
#
# total, error_msg = get_aftersale_orders(
#     store_id, store_detail, start_stamp,
#     end_stamp, order_detail_callback)
# # 测试获取商品信息
# get_wares(store_id, store_detail, start_stamp, end_stamp, ware_detail_callback)

# 测试订单发货
# order_id = '3770041015076186946'
# order_detail, order_error_msg = get_order_detail(store_detail, order_id)
# express_list, error_msg = get_express_list()
# express_name = "申通快递"
# deliver_no = "314672521551"
# express_code = express_list.get(express_name, None)
# express_code = "STO"
# 整单发货
# deliver_success, delivery_error_msg = order_delivery(store_detail, order_id, express_code, deliver_no)
# jOrderGoodsIds = ""
# jOrderGiftIds = ""
# for item in order_detail["goodslist"]:
#     if item["isgift"] == 1:
#         if len(jOrderGiftIds) == 0:
#             jOrderGiftIds += item["ordergoodsid"]
#         else:
#             jOrderGiftIds += "," + item["ordergoodsid"]
#     else:
#         if len(jOrderGoodsIds) == 0:
#             jOrderGoodsIds += item["ordergoodsid"]
#         else:
#             jOrderGoodsIds += "," + item["ordergoodsid"]
#     break
#
# skus_param = {
#     "jOrderGoodsIds": jOrderGoodsIds,
#     "jOrderGiftIds": jOrderGiftIds
# }
# # 部分发货
# deliver_success, error_msg = order_delivery_split(
#     store_detail, order_id, express_code, deliver_no, skus_param)
