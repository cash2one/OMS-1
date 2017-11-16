#!/usr/bin/python3
#  -*- coding: utf-8 -*-
import time
from oms_server.services.platforms import common_params

oms_goods = {
    "user_id": "",
    "item_code": "",
    "outer_item_code": "",
    "sku_name": "",
    "specification": "",
    "bar_code": "",
    # "user_code": "",
    "price": "",
    "unit": "",
    "goods_no": "",
    "sku_version": "",
    "item_type": "",
    "brand": "",
    "brand_name": "",
    "color": "",
    "size": "",
    "gross_weight": "",
    "net_weight": "",
    "length": "",
    "width": "",
    "height": "",
    "volume": "",
    "pcs": "",
    # "quantity": "",
    # "available_quantity": "",
    "is_shelflife": "",
    "lifecycle": "",
    "reject_lifecycle": "",
    "lockup_lifecycle": "",
    "advent_lifecycle": "",
    "is_sn_mgt": "",
    "is_hygroscopic": "",
    "is_danger": "",
    "category": "",
    "category_name": "",
}


def refresh_token(platform_name, store_detail, timeout=common_params.TIMEOUT):
    platform = __import__(
        'oms_server.services.platforms.' +
        platform_name,
        fromlist=[''])
    access_token = None
    error_msg = None
    if platform:
        access_token, error_msg = platform.refresh_token(store_detail, timeout)
    return access_token, error_msg


def get_ware_total(
        platform_name, store_detail, start_stamp, end_stamp):
    platform = __import__(
        'oms_server.services.platforms.' +
        platform_name,
        fromlist=[''])
    total_num = 0
    error_msg = None
    if platform:
        total_num, error_msg = platform.get_ware_total(store_detail, start_stamp, end_stamp)
    return total_num, error_msg


# def get_ware_list(
#         platform_name,
#         store_detail,
#         pageno,
#         pagesize=common_params.PAGE_SIZE):
#     platform = __import__(
#         'oms_server.services.platforms.' +
#         platform_name,
#         fromlist=[''])
#     if platform:
#         return platform.get_ware_list(store_detail, pageno, pagesize)
#
#
# def to_oms_sku(platform_name, user_id, detail):
#     platform = __import__(
#         'oms_server.services.platforms.' +
#         platform_name,
#         fromlist=[''])
#     if platform:
#         return platform.to_oms_sku(user_id, detail)

def get_wares(
        platform_name, user_param, store_detail,
        start_stamp, end_stamp, callback=None):
    platform = __import__(
        'oms_server.services.platforms.' + platform_name,
        fromlist=[''])
    if platform:
        return platform.get_wares(user_param, store_detail, start_stamp, end_stamp, callback)


def get_orders(
        platform_name, user_param, store_detail,
        start_stamp, end_stamp, callback=None):
    platform = __import__(
        'oms_server.services.platforms.' + platform_name,
        fromlist=[''])
    if platform:
        return platform.get_orders(user_param, store_detail, start_stamp, end_stamp, callback)


# 订单发货处理 express_code：快递公司代码；deliver_no：快递单号；
def order_delivery(platform_name, store_detail, order_id,
                   express_code, deliver_no, item_details=None):
    platform = __import__(
        'oms_server.services.platforms.' +
        platform_name,
        fromlist=[''])
    if platform:
        return platform.order_delivery(store_detail, order_id,
                                       express_code, deliver_no, item_details)
    return False, ''


# def get_wares(
#         platform_name,
#         goods_num,
#         store_detail,
#         pagesize=common_params.PAGE_SIZE,
#         timeout=common_params.TIMEOUT):
#     platform = __import__('oms.goods.' + platform_name, fromlist=[''])
#     if platform:
#         platform.get_wares(
#             goods_num, store_detail, pagesize, timeout)


'''=========================test code========================='''
# store_detail = {
#     "app_key": "c59d6819e6ccccac38",
#     "app_secret": "99779bea68051ce8fd84164a2bbc2113",
#     "access_token": "61abf9405f2d3688ab63ff427df1fd1a",
#     "store_key": "19378592",
#     "expire_in": "",
#     "platform_name": "youzan",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }
# store_detail = {
#     "app_key": "685719",
#     "app_secret": "a840c46a16c572a9b6c93e30f14dbaeb",
#     "access_token": "a07c18f7e27abae54aa9608bbfffa97a00076714de",
#     "store_key": "",
#     "platform_name": "weidian",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }
# store_detail = {
#     "app_key": "685338",
#     "app_secret": "9a88ac61537de03945669d8b50193077",
#     "access_token": "adcc5eac80d57d6b44e958937ff3c8cd00076332cd",
#     "store_key": "",
#     "platform_name": "weidian",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }
# store_detail = {
#     "access_token": "2e17c479-a024-47c0-9d56-b5cc80592a7e",
#     "app_key": "6B95AD6AB566DDB87946374E26021AB6",
#     "app_secret": "f2ad5ba1a4e347a1b7f0108cdf6ab1ac",
#     "store_key": "",
#     "refresh_token": "3fc22a38-7729-4b37-8084-de2d8ebaaac0",
#     "platform_name": "jingdong",
#     "user_id": "93696c16-6654-4e14-b215-838295b1a7c5",
#     "store_is_auto_check": True
# }

# refresh_token(store_detail["platform_name"], store_detail)
# order_id = '800170211512979'
# express_code = 'SF'
# deliver_no = "314672521551"
# skus_param = []
#
# order_delivery_split(platform_name, store_detail, order_id,
#                      express_code, deliver_no, skus_param)
# user_id = '795298230f4442209274e2a2dae41f84'
# goods_num = get_ware_total(platform_name, store_detail)
# pages = params.get_pages(goods_num)
# index = 0
# for i in range(pages):
#     pageno = i + 1
#     ware_page = get_ware_list(
#         platform_name, store_detail, pageno)
#     for ware in ware_page:
#         sku_list = to_oms_sku(platform_name, user_id, ware)
#         for sku in sku_list:
#             print(sku)


# def ware_detail_callback(user_param, sku, wares_total, sku_number, is_end):
#     if is_end:
#         print("共计%s个商品，%s个SKU" % (wares_total, sku_number))
#     else:
#         print(
#             "商品编号 = %s, 商品名称 = %s 商品价格 = %s" %
#             (sku["item_code"],
#              sku["sku_name"],
#              sku["price"]))
#
#
# def start_pull_wares(store_detail, start_stamp, end_stamp):
#     if "platform_name" in store_detail:
#         platform = __import__('.' + store_detail["platform_name"], fromlist=[''])
#         if platform:
#             platform.get_wares(store_detail,
#                                start_stamp, end_stamp,
#                                callback=ware_detail_callback)
#
#
# # start_pull_orders(stores)
# start_time = "2017-10-26 0:0:0"
# start_stamp = time.mktime(time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))
# end_stamp = time.time()
# start_pull_wares(store_detail, start_stamp, end_stamp)
