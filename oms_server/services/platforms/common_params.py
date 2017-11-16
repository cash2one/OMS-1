# -*- coding: utf-8 -*-

PAGE_SIZE = 50
TIMEOUT = 15     # 秒
HOUR_1 = 60*60
DAY_1 = HOUR_1*24
MONTH_1 = DAY_1*30
DAY_90 = DAY_1*90
YEAR_1 = DAY_1*365

OBTAIN_DATA_FAILED = "获取数据失败"


oms_sku = {
    "user_id": "",
    "item_code": "",
    "outer_item_code": "",
    "sku_name": "",
    "specification": "",
    "bar_code": "",
    # "user_code": "",
    "price": float(0.0),
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
    # "quantity": int(0),
    # "available_quantity": int(0),
    "is_shelflife": False,
    "lifecycle": 0,
    "reject_lifecycle": 0,
    "lockup_lifecycle": 0,
    "advent_lifecycle": 0,
    "is_sn_mgt": False,
    "is_hygroscopic": False,
    "is_danger": False,
    "category": "",
    "category_name": "",
}


def get_pages(total, pagesize=PAGE_SIZE):
    pages = total // pagesize
    if total % pagesize:
        pages += 1
    return pages


def get_short_name(filename):
    import os
    (filepath, tempfilename) = os.path.split(filename)
    (shotname, extension) = os.path.splitext(tempfilename)
    return shotname
