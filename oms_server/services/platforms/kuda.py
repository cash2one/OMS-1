import time
import json
import urllib.parse
from uuid import uuid4
from oms_server.services.platforms import requests_util
from oms_server.services.platforms import common_params
from oms_server.services.platforms import kuda_data


DOMAIN = {
    # 沙箱环境
    # "api": "http://test.kucangbao.com/kcb-1.0/tbserver?",
    "api": "http://test1.kucangbao.com/tbserver?",
    # 正式环境
    # "api": "http://open.juanpi.com/erpapi/index",
    "get_express": "http://open.juanpi.com/erpapi/get_express",

    "oauth": "http://61.183.199.130:2016/erpapi/authorize/erpapi/index?"
}


# 获取订单详细
def get_order_detail(store_detail, order_id):
    # update_end = time.strftime("%Y-%m-%d%H:%M:%S", time.localtime(end_stamp))
    # update_start = time.strftime(
    #     "%Y-%m-%d%H:%M:%S",
    #     time.localtime(start_stamp))
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    url = DOMAIN["api"]
    param_json = {
        "tid": order_id,
        "nick": store_detail["store_key"],
        # "fromModified": update_start,
        # "toModified": update_end,
        "status": -1,
    }
    app_params = {
        "method": "getTrade",
        "access_key": store_detail["app_key"],
        "access_token": store_detail["access_token"],
        "timestamp": current_date,
        "format": "json",
        "v": "1.0",
        "param_json": param_json,
    }
    params = urllib.parse.urlencode(app_params)
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    error_msg = None
    if "msg" in res:
        if len(res["msg"]) != 0:
            error_msg = res["msg"]
    if "error_response" in res:
        error_msg = res["error_response"]
    if "info" in res:
        if res["info"].isdigit():
            error_msg = res["info"]
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
        pagesize):
    update_end = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_stamp))
    update_start = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(start_stamp))
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    url = DOMAIN["api"]
    param_json = {
        # "tid": "",
        "nick": store_detail["store_key"],
        "fromModified": update_start,
        "toModified": update_end,
        "status": -1,
        "page": pageno - 1,
        "limit": pagesize,
    }
    app_params = {
        "method": "getTrade",
        "access_key": store_detail["app_key"],
        "access_token": store_detail["access_token"],
        "timestamp": current_date,
        "v": "1.0",
        "format": "json",
        "param_json": param_json,
    }
    params = urllib.parse.urlencode(app_params)
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return ""
    res = json.loads(resp.text)
    # res = kuda_data.orders
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
    order_list = ""
    if "msg" in res:
        if len(res["msg"]) != 0:
            error_msg = res["msg"]
    if "jsons" in res:
        order_list = res["jsons"]
    return order_list, error_msg


def get_order_total(store_detail, start_stamp, end_stamp):
    res = get_order_response(store_detail, start_stamp, end_stamp, 1, 1)
    error_msg = None
    order_total = 0
    if "msg" in res:
        if len(res["msg"]) != 0:
            error_msg = res["msg"]
    if "total" in res:
        order_total = int(res["total"])
    return order_total, error_msg


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
        for item in order_list:
            order_detail = None
            if "trade_fullinfo_get_response" in item and "trade" in item[
                    "trade_fullinfo_get_response"]:
                order_detail = item["trade_fullinfo_get_response"]["trade"]
            if order_detail is None:
                continue
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
    return total, error_msg


def transfer_order(raw_order, prefix):
    order = {}

    order["order_id"] = str(uuid4())
    order["order_code_oms"] = prefix + "_" + str(raw_order["tid"])

    # 支付方式 1：卷皮充值 2：支付宝 3：银联 4：财 付通 5：支付宝手机版 6：支付宝 pc7：客户端微 信 8：wap 微信 9：pc 微信
    order["order_type"] = raw_order["type"]
    order["order_code"] = raw_order["tid"]  # 交易编号
    order["total_price"] = raw_order["total_fee"]  # 总价格
    order["goods_price"] = raw_order["price"]  # 商品单价
    order["quantity"] = raw_order["num"]  # 商品数量

    order["express_number"] = ""
    order["express_fee"] = 0.0
    # free(卖家包邮), post(平邮), express(快递), ems(EMS),
    # virtual(虚拟发货)，25(次日必达)，26(预约配送)
    order["express_type"] = raw_order["shipping_type"]
    order["express_note"] = ""

    order["status"] = 10
    order["order_status_info"] = ""

    order["status_ori"] = order_status_pair[str(
        raw_order["status"])]  # 订单状态 枚举值
    order["refund_status_ori"] = 0  # 退款状态'''
    if "orders" in raw_order and "order" in raw_order["orders"]:
        info_list = raw_order["orders"]["order"]
        expect_success_total = len(info_list)
        real_success_total = 0
        for item in info_list:
            if order_refund_status_pair[item["refund_status"]] == 1:
                real_success_total += 1
                order["refund_status_ori"] = order_refund_status_pair[item["refund_status"]]
        if real_success_total:
            if real_success_total == expect_success_total:
                order["refund_status_ori"] = 1
            else:
                order["refund_status_ori"] = 2

    order["buyer_note"] = ""
    if "buyer_message" in raw_order:
        order["buyer_note"] = raw_order["buyer_message"]  # 买家留言
    order["seller_note"] = ""
    if "seller_memo" in raw_order:
        order["seller_note"] = raw_order["seller_memo"]  # 卖家备注

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
    details = raw_order["orders"]["order"]
    for detail in details:
        order_detail = {}
        order_detail["order_detail_id"] = str(uuid4())  # 唯一编码
        order_detail["sku_id"] = ""  # str(uuid1())
        order_detail["order_id"] = order["order_id"]  # 订单编号
        order_detail["item_code"] = detail["sku_id"]
        if len(detail["outer_sku_id"]):
            order_detail["item_code"] = detail["outer_sku_id"]  # 交易明细编号
        order_detail["price"] = float(detail["price"])
        order_detail["quantity"] = int(detail["num"])
        order_detail["total_price"] = float(detail["total_fee"])

        order_detail["is_gift"] = False
        order_detail["is_exist"] = True

        order_details.append(order_detail)

    order["order_details"] = order_details
    return order


order_status_pair = {
    # 0元购合约中
    "WAIT_PRE_AUTH_CONFIRM": 0,
    # 国际信用卡支付付款确认中
    "PAY_PENDING": 0,
    # 没有创建支付宝交易
    "TRADE_NO_CREATE_PAY": 0,
    # 等待买家付款
    "WAIT_BUYER_PAY": 0,
    # 拼团中订单，已付款但禁止发货
    "PAID_FORBID_CONSIGN": 0,

    # 等待卖家发货,即:买家已付款
    "WAIT_SELLER_SEND_GOODS": 10,

    # 卖家部分发货
    "SELLER_CONSIGNED_PART": 21,
    # 等待买家确认收货,即:卖家已发货
    "WAIT_BUYER_CONFIRM_GOODS": 20,

    # 买家已签收,货到付款专用
    "TRADE_BUYER_SIGNED": 30,
    # 部分发货(同备货中，即将废除)
    "10": 31,

    # 交易成功
    "TRADE_FINISHED": -1,
    # 付款以后用户退款成功，交易自动关闭
    "TRADE_CLOSED": -1,
    # 付款以前，卖家或买家主动关闭交易
    "TRADE_CLOSED_BY_TAOBAO": -1,
}


order_refund_status_pair = {
    "NO_REFUND": 0,

    # 买家已经申请退款，等待卖家同意
    "WAIT_SELLER_AGREE": 100,
    # 卖家已经同意退款，等待买家退货
    "WAIT_BUYER_RETURN_GOODS": 100,
    # 买家已经退货，等待卖家确认收货
    "WAIT_SELLER_CONFIRM_GOODS": 100,
    # 卖家拒绝退款
    "SELLER_REFUSE_BUYER": 100,

    # 退款关闭
    "CLOSED": -1,
    # 退款成功
    "SUCCESS": 1,
}


def get_ware_detail(store_detail, ware_id):
    url = DOMAIN["api"]
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    param_json = {
        "numiid": ware_id,
        "nick": store_detail["store_key"],
    }
    app_params = {
        "method": "getItem",
        "access_key": store_detail["app_key"],
        "access_token": store_detail["access_token"],
        "timestamp": current_date,
        "format": "json",
        "v": "1.0",
        "param_json": param_json,
    }

    params = urllib.parse.urlencode(app_params)
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)

    error_msg = None
    ware_detail = {}
    if "json" in res and "item_get_response" in res["json"]:
        response = res["json"]["item_get_response"]
        if "item" in response:
            ware_detail = response["item"]
    return ware_detail, error_msg


def get_ware_reponse(
        store_detail,
        start_stamp,
        end_stamp,
        pageno,
        pagesize):
    update_end = time.strftime("%Y-%m-%d%H:%M:%S", time.localtime(end_stamp))
    update_start = time.strftime(
        "%Y-%m-%d%H:%M:%S",
        time.localtime(start_stamp))
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    url = DOMAIN["api"]
    param_json = {
        # "tid": "",
        "nick": store_detail["store_key"],
        "fromModified": update_start,
        "toModified": update_end,
        # "status": -1,
        "page": pageno,
        "limit": pagesize,
    }
    app_params = {
        "method": "getItem",
        "access_key": store_detail["app_key"],
        "access_token": store_detail["access_token"],
        "timestamp": current_date,
        "format": "json",
        "v": "1.0",
        "param_json": param_json,
    }
    params = urllib.parse.urlencode(app_params)
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return ""
    res = json.loads(resp)
    # res = kuda_data.wares
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
    if "jsons" in res:
        ware_list = res["jsons"]
    return ware_list, error_msg


def get_ware_total(store_detail, start_stamp, end_stamp):
    res = get_ware_reponse(store_detail, start_stamp, end_stamp, 1, 1)
    error_msg = None
    total_num = 0
    if "total" in res:
        total_num = int(res["total"])
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
        for item in ware_list:
            ware_detail = None
            if "item_get_response" in item:
                ware_detail = item["item_get_response"]
            if ware_detail is None:
                continue
            sku_list = to_oms_sku(
                store_detail["user_id"], ware_detail)
            if isinstance(sku_list, list):
                for sku in sku_list:
                    if callback:
                        if index == 0:
                            status["callback_status"] = "start"
                            status["start_stamp"] = time.time()
                        index += 1
                        callback(
                            user_param,
                            store_detail,
                            sku,
                            total,
                            index,
                            status)
    if callback:
        status["callback_status"] = "end"
        status["end_stamp"] = time.time()
        callback(user_param, store_detail, None, total, index, status)
        return total, error_msg


def to_oms_sku(user_id, ware):
    skus = []
    if isinstance(ware, list):
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
    if isinstance(ware, dict):
        item = ware["item"]
        sku = {
            "user_id": str(user_id),
            "item_code": str(item["num_iid"]),
            "outer_item_code": item["outer_id"],
            "sku_name": str(item["title"]),
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


def order_decrypt(store_detail, data):
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    url = DOMAIN["api"]
    param_json = {
        "jsons": data,
        "nick": store_detail["store_key"],
    }
    app_params = {
        "method": "decrypt",
        "access_key": store_detail["app_key"],
        "access_token": store_detail["access_token"],
        "timestamp": current_date,
        "format": "json",
        "v": "1.0",
        "param_json": param_json,
    }
    params = urllib.parse.urlencode(app_params)
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    result = None
    error_msg = None
    if "success" in res:
        error_msg = res["msg"]
    if "jsons" in res:
        result = res["jsons"]
    return result, error_msg


# 订单发货处理 express_code：快递公司代码；deliver_no：快递单号；
def order_delivery(
        store_detail,
        order_id,
        express_code,
        deliver_no,
        item_details=None):
    express = transfer_express.get(express_code)
    now = time.time()
    current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
    url = DOMAIN["api"]
    param_json = {
        "tid": order_id,
        "nick": store_detail["store_key"],
        # 0：线下发货 1：线上发货 2：虚拟发货
        "sendway": 1,
        "companycode": express["code"],
        "outsid": deliver_no,
    }
    app_params = {
        "method": "taobaoSend",
        "access_key": store_detail["app_key"],
        "access_token": store_detail["access_token"],
        "timestamp": current_date,
        "format": "json",
        "v": "1.0",
        "param_json": param_json,
    }
    params = urllib.parse.urlencode(app_params)
    resp = requests_util.get(url=url, params=params)
    if not resp:
        return "", common_params.OBTAIN_DATA_FAILED
    res = json.loads(resp.text)
    # res = kuda_data.delivery
    result = None
    error_msg = None
    if "shipping" in res:
        error_msg = res["msg"]
    if "success" in res:
        result = res["success"]
    return result, error_msg


# 淘宝返回的原始物流公司
taobao_express = {
    "logistics_companies": {
        "logistics_company": [
            {
                "code": "HOAU",
                "id": 1191,
                "name": "天地华宇",
                "reg_mail_no": "^[A-Za-z0-9]{8,9}$"
            },
            {
                "code": "DTW",
                "id": 512,
                "name": "大田"
            },
            {
                "code": "HTKY",
                "id": 502,
                "name": "百世快递",
                "reg_mail_no": "^((A|B|D|E)[0-9]{12})$|^(BXA[0-9]{10})$|^(K8[0-9]{11})$|^(02[0-9]{11})$|"
                               "^(000[0-9]{10})$|^(C0000[0-9]{8})$|^((21|22|23|24|25|26|27|28|29|30|31|32|"
                               "33|34|35|36|37|38|39|61|63)[0-9]{10})$|^((50|51)[0-9]{12})$|^7[0-9]{13}$|"
                               "^6[0-9]{13}$|^58[0-9]{14}$"
            },
            {
                "code": "YTO",
                "id": 101,
                "name": "圆通速递",
                "reg_mail_no": "^[A-Za-z0-9]{2}[0-9]{10}$|^[A-Za-z0-9]{2}[0-9]{8}$|^(8)[0-9]{17}|^(9)[0-9]{17}$"
            },
            {
                "code": "STO",
                "id": 100,
                "name": "申通快递",
                "reg_mail_no": "^(268|888|588|688|368|468|568|668|768|868|968)[0-9]{9}$|^(11|22|40|268|888|588|"
                               "688|368|468|568|668|768|868|968)[0-9]{10}$|^(STO)[0-9]{10}$|^(33)[0-9]{11}$|"
                               "^(4)[0-9]{12}$|^(55)[0-9]{11}$|^(66)[0-9]{11}$|^(77)[0-9]{11}$|^(88)[0-9]{11}$|"
                               "^(99)[0-9]{11}$"
            },
            {
                "code": "SF",
                "id": 505,
                "name": "顺丰速运",
                "reg_mail_no": "^[A-Za-z0-9-]{4,35}$"
            },
            {
                "code": "EMS",
                "id": 2,
                "name": "EMS",
                "reg_mail_no": "^[A-Z]{2}[0-9]{9}[A-Z]{2}$|^(10|11)[0-9]{11}$|^(50|51)[0-9]{11}$|^(95|97)[0-9]{11}$"
            },
            {
                "code": "ZJS",
                "id": 103,
                "name": "宅急送",
                "reg_mail_no": "^[a-zA-Z0-9]{10}$|^(42|16)[0-9]{8}$|^A[0-9]{12}"
            },
            {
                "code": "YUNDA",
                "id": 102,
                "name": "韵达快递",
                "reg_mail_no": "^(10|11|12|13|14|15|16|17|19|18|50|55|58|80|88|66|31|77|39)[0-9]{11}$|^[0-9]{13}$"
            },
            {
                "code": "ZTO",
                "id": 500,
                "name": "中通快递",
                "reg_mail_no": "^((765|852|779|359|528|751|358|618|680|778|780|768|688|689|618|828|988|118|"
                               "128|888|571|518|010|628|205|880|717|718|728|738|761|762|763|701|757|719|881|120)"
                               "[0-9]{9})$|^((2008|2010|8050|7518)[0-9]{8})$|^((36|37|53)[0-9]{10})$|^((4)[0-9]{11})$"
            },
            {
                "code": "POST",
                "id": 1,
                "name": "中国邮政"
            },
            {
                "code": "OTHER",
                "id": -1,
                "name": "其他",
                "reg_mail_no": "^[A-Za-z0-9-]{4,35}$"
            },
            {
                "code": "AIR",
                "id": 507,
                "name": "亚风",
                "reg_mail_no": "^[0-9]{11}$"
            },
            {
                "code": "DISTRIBUTOR_1710055",
                "id": 5000000178661,
                "name": "邮政标准快递",
                "reg_mail_no": "^(10)[0-9]{11}$|^(11)[0-9]{11}$"
            },
            {
                "code": "MGSD",
                "id": 21000007003,
                "name": "美国速递"
            },
            {
                "code": "BHWL",
                "id": 21000053037,
                "name": "保宏物流"
            },
            {
                "code": "DISTRIBUTOR_13211725",
                "id": 1216000000124268,
                "name": "跨越速运",
                "reg_mail_no": ""
            },
            {
                "code": "UNIPS",
                "id": 1237,
                "name": "发网"
            },
            {
                "code": "YUD",
                "id": 513,
                "name": "长发"
            },
            {
                "code": "DISTRIBUTOR_13159132",
                "id": 6000100034186,
                "name": "菜鸟大件-日日顺配",
                "reg_mail_no": "^[0-9-]{10,20}$|^\\d{15,}[-\\d]+$"
            },
            {
                "code": "YC",
                "id": 1139,
                "name": "远长",
                "reg_mail_no": "^96[0-9]{12}$"
            },
            {
                "code": "DISTRIBUTOR_13148625",
                "id": 6000100034229,
                "name": "菜鸟大件-中铁配",
                "reg_mail_no": "^\\d{15,}[-\\d]+$|^[0-9]{10}|[0-9]{12}$"
            },
            {
                "code": "DISTRIBUTOR_13222803",
                "id": 1216000000125358,
                "name": "中通快运"
            },
            {
                "code": "DFH",
                "id": 1137,
                "name": "东方汇",
                "reg_mail_no": "^[0-9]{10}$|^LBX[0-9]{15}-[2-9AZ]{1}-[1-9A-Z]{1}"
            },
            {
                "code": "CYEXP",
                "id": 511,
                "name": "长宇"
            },
            {
                "code": "WND",
                "id": 21000127009,
                "name": "WnDirect",
                "reg_mail_no": ""
            },
            {
                "code": "GZLT",
                "id": 200427,
                "name": "飞远配送 "
            },
            {
                "code": "PKGJWL",
                "id": 21000038002,
                "name": "派易国际物流77"
            },
            {
                "code": "BESTQJT",
                "id": 105031,
                "name": "百世快运"
            },
            {
                "code": "NEDA",
                "id": 1192,
                "name": "能达速递",
                "reg_mail_no": "^((88|)[0-9]{10})$|^((1|2|3|5|)[0-9]{9})$|^(90000[0-9]{7})$"
            },
            {
                "code": "YCT",
                "id": 1185,
                "name": "黑猫宅急便",
                "reg_mail_no": "^[0-9]{12}$"
            },
            {
                "code": "SURE",
                "id": 201174,
                "name": "速尔",
                "reg_mail_no": "^[0-9]{11}[0-9]{1}$"
            },
            {
                "code": "DBL",
                "id": 107,
                "name": "德邦物流",
                "reg_mail_no": "^[0-9]{8,10}$|^\\d{15,}[-\\d]+$"
            },
            {
                "code": "UC",
                "id": 1207,
                "name": "优速快递",
                "reg_mail_no": "^VIP[0-9]{9}|V[0-9]{11}|[0-9]{12}$|"
                               "^LBX[0-9]{15}-[2-9AZ]{1}-[1-9A-Z]{1}$|^(9001)[0-9]{8}$"
            },
            {
                "code": "LTS",
                "id": 1214,
                "name": "联昊通",
                "reg_mail_no": "^[0-9]{9,12}$"
            },
            {
                "code": "ESB",
                "id": 200740,
                "name": "E速宝",
                "reg_mail_no": "[0-9a-zA-Z-]{5,20}"
            },
            {
                "code": "GTO",
                "id": 200143,
                "name": "国通快递",
                "reg_mail_no": "^(3(([0-6]|[8-9])\\d{8})|((2|4|5|6|7|8|9)\\d{9})|(1|2|3|4|5|6|7|8|9)\\d{11})$"
            },
            {
                "code": "LB",
                "id": 1195,
                "name": "龙邦速递",
                "reg_mail_no": "^[0-9]{12}$|^LBX[0-9]{15}-[2-9AZ]{1}-[1-9A-Z]{1}$|^[0-9]{15}$|^[0-9]{15}"
                               "-[1-9A-Z]{1}-[1-9A-Z]{1}$"
            },
            {
                "code": "POSTB",
                "id": 200734,
                "name": "邮政快递包裹",
                "reg_mail_no": "^([GA]|[KQ]|[PH]){2}[0-9]{9}([2-5][0-9]|[1][1-9]|[6][0-5])$|"
                               "^[99]{2}[0-9]{11}$|^[96]{2}[0-9]{11}$|^[98]{2}[0-9]{11}$"
            },
            {
                "code": "TTKDEX",
                "id": 504,
                "name": "天天快递",
                "reg_mail_no": "^[0-9]{12}$"
            },
            {
                "code": "HZABC",
                "id": 1121,
                "name": "飞远(爱彼西)配送",
                "reg_mail_no": "^[0-9]{10,11}$|^T[0-9]{10}$|^FYPS[0-9]{12}$|^LBX[0-9]{15}-[2-9AZ]{1}-[1-9A-Z]{1}$"
            },
            {
                "code": "EYB",
                "id": 3,
                "name": "EMS经济快递",
                "reg_mail_no": "^[A-Z]{2}[0-9]{9}[A-Z]{2}$|^(10|11)[0-9]{11}$|^(50|51)[0-9]{11}$|^(95|97)[0-9]{11}$"
            },
            {
                "code": "DBKD",
                "id": 5000000110730,
                "name": "德邦快递",
                "reg_mail_no": "^[0-9]{8,10}$|^\\d{15,}[-\\d]+$"
            },
            {
                "code": "CNEX",
                "id": 1056,
                "name": "佳吉快递",
                "reg_mail_no": "^[7,1,9][0-9]{9}$"
            },
            {
                "code": "QFKD",
                "id": 1216,
                "name": "全峰快递",
                "reg_mail_no": "^[0-6|9][0-9]{11}$|^[7][0-8][0-9]{10}$|^[0-9]{15}$|^[S][0-9]{9,11}"
                               "(-|)P[0-9]{1,2}$|^[0-9]{13}$|^[8][0,2-9][0,2-9][0-9]{9}$|^[8][1]"
                               "[0,2-9][0-9]{9}$|^[8][0,2-9][0-9]{10}$|^[8][1][1][0][8][9][0-9]{6}$"
            },
            {
                "code": "GDEMS",
                "id": 1269,
                "name": "广东EMS",
                "reg_mail_no": "^[a-zA-Z]{2}[0-9]{9}[a-zA-Z]{2}$"
            },
            {
                "code": "FEDEX",
                "id": 106,
                "name": "联邦快递",
                "reg_mail_no": "^[0-9]{12}$"
            },
            {
                "code": "QRT",
                "id": 1208,
                "name": "增益速递",
                "reg_mail_no": "^[0-9]{12,13}$"
            },
            {
                "code": "UAPEX",
                "id": 1259,
                "name": "全一快递",
                "reg_mail_no": "^\\d{12}|\\d{11}$"
            },
            {
                "code": "XB",
                "id": 1186,
                "name": "新邦物流",
                "reg_mail_no": "[0-9]{8}"
            },
            {
                "code": "BJRFD-001",
                "id": 100034107,
                "name": "如风达配送",
                "reg_mail_no": "^[\\x21-\\x7e]{1,100}$"
            },
            {
                "code": "XFWL",
                "id": 202855,
                "name": "信丰物流",
                "reg_mail_no": "^130[0-9]{9}|13[7-9]{1}[0-9]{9}|18[8-9]{1}[0-9]{9}$"
            },
            {
                "code": "FAST",
                "id": 1204,
                "name": "快捷快递",
                "reg_mail_no": "^(?!440)(?!510)(?!520)(?!5231)([0-9]{9,13})$|^(P330[0-9]{8})$|^(D[0-9]"
                               "{11})$|^(319)[0-9]{11}$|^(56)[0-9]{10}$|^(536)[0-9]{9}$"
            },
            {
                "code": "SHQ",
                "id": 108,
                "name": "华强物流",
                "reg_mail_no": "^[A-Za-z0-9]*[0|2|4|6|8]$"
            },
            {
                "code": "BEST",
                "id": 105,
                "name": "百世物流",
                "reg_mail_no": "^[0-9]{11,12}$"
            }
        ]
    }
}


transfer_express = {
    # 顺丰
    'SF': {
        "code": "SF",
        "id": 505,
        "name": "顺丰速运",
    },
    # 标准快递
    'EMS': {
        "code": "EMS",
        "id": 2,
        "name": "EMS",
    },
    #
    'EYB': {
        "code": "EYB",
        "id": 3,
        "name": "EMS经济快递",
    },
    # 宅急送
    'ZJS': {
        "code": "ZJS",
        "id": 103,
        "name": "宅急送",
    },
    # 圆通
    'YTO': {
        "code": "YTO",
        "id": 101,
        "name": "圆通速递",
    },
    # 中通(ZTO)
    'ZTO': {
        "code": "ZTO",
        "id": 500,
        "name": "中通快递",
    },
    # 百世汇通
    'HTKY': {
        "code": "HTKY",
        "id": 105031,
        "name": "百世快运"
    },
    # 优速
    'UC': {
        "code": "UC",
        "id": 1207,
        "name": "优速快递",
    },
    #
    'STO': {
        "code": "STO",
        "id": 100,
        "name": "申通快递",
    },
    # 天天快递
    'TTKDEX': {
        "code": "TTKDEX",
        "id": 504,
        "name": "天天快递",
    },
    # 全峰
    'QFKD': {
        "code": "QFKD",
        "id": 1216,
        "name": "全峰快递",
    },
    # 快捷
    'FAST': {
        "code": "FAST",
        "id": 1204,
        "name": "快捷快递",
    },
    # 邮政小包
    'POSTB': {
        "code": "POSTB",
        "id": 200734,
        "name": "邮政快递包裹",
    },
    # 国通
    'GTO': {
        "code": "GTO",
        "id": 200143,
        "name": "国通快递",
    },
    # 韵达
    "YUNDA": {
        "code": "YUNDA",
        "id": 102,
        "name": "韵达快递",
    },
    # 京东配送
    'JD': None,
    # 当当宅配
    'DD': None,
    # 亚马逊物流
    'AMAZON': None,
}


# TODO 测试
'''=========================test code========================='''
# store_detail = {
#     "platform_id": 2,
#     "platform_name": "kuda",
#     "store_key": "691764",
#     "app_key": "8D311921DE6B681D671AC7F3C52B96D6",
#     "app_secret": "85d0c2caf3c449d08751b44ef7316df1",
#     "access_token": "b62953c7-d618-4d4d-990b-e1b8b58c5c7b",
#     "refresh_token": "d1aae42b-b0ea-4697-85f5-c1523afa1cd6",
#     "id": "st1000000110001",
#     "user_id": 10000001,
#     "last_get_order_at": "2017-11-2 16:00:00",
#     "store_is_auto_check": True,
# }
# start_time = store_detail["last_get_order_at"]
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()
