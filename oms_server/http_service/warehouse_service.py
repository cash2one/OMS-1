import requests
from django.conf import settings
from oms_server.extension.http_utils import get
from oms.extension.exception import CustomException
# 47.95.235.167:8002
# GET_WAREHOUSE_BY_ID_URL =\
#     'http://47.95.235.167:8002/api/users/warehouses/'
# GET_WAREHOUSE_BY_CODE_URL =\
#     'http://47.95.235.167:8002/api/warehouses/warehouse_info'
# LIST_AVAILABLIE_WAREHOUSE_URL =\
#     'http://47.95.235.167:8002/api/users/available_warehouses'
# LIST_OWN_WAREHOUSE_URL =\
#     'http://47.95.235.167:8002/api/users/own_warehoues'
# GET_ALL_USER_WAREHOUSES =\
#     'http://47.95.235.167:8002/api/users/user_warehouses'
GET_SHARED_WAREHOUSE_OPERATION_INFO = '/api/operation_info/shared'
GET_USED_WAREHOUSE_OPERATION_INFO = '/api/operation_info/used'
#settings.CMM_URL


def get_shared_warehouse_operation_info(warehouse_id, token):
    headers = {'token': token}
    param = {'warehouse_id': warehouse_id}
    resp = requests.get(
        settings.CMM_URL+GET_SHARED_WAREHOUSE_OPERATION_INFO,
        params=param,
        headers=headers)
    print(resp)
    resp = resp.json()
    if resp and resp['result'] is not None:
        return resp['result']
    elif not resp['result']:
        raise CustomException(10010, '获取不到仓库信息')
    return None


def get_used_warehouse_operation_info(warehouse_id, token):
    headers = {'token': token}
    param = {'warehouse_id': warehouse_id}
    resp = requests.get(
        settings.CMM_URL+GET_USED_WAREHOUSE_OPERATION_INFO,
        params=param,
        headers=headers)
    print(resp)
    resp = resp.json()
    if resp and resp['result'] is not None:
        return resp['result']
    elif not resp['result']:
        raise CustomException(10010, '获取不到仓库信息')
    return None


def get_warehouse_by_id(warehouse_id, token=None):
    headers = {}
    if token:
        headers = {'token': token}
    resp = get(settings.GET_WAREHOUSE_BY_ID_URL + warehouse_id, headers=headers)
    if resp and resp['result'] is not None:
        return transfer_warehouse(resp['result'])
    elif not resp['result']:
        raise CustomException(10010, '获取不到仓库信息')
    return None


def get_warehouse_by_code(warehouse_code, wms_app_key, token=None):
    headers = {}
    if token:
        headers = {'token': token}

    param = {'warehouse_code': warehouse_code, 'wms_app_key': wms_app_key}
    resp = requests.get(settings.GET_WAREHOUSE_BY_CODE_URL, params=param,  headers=headers)
    print(resp)
    resp = resp.json()
    if resp and resp['result'] is not None:
        return transfer_warehouse(resp['result'])
    elif not resp['result']:
        raise CustomException(10010, '获取不到仓库信息')
    return None


def list_available_warehouse(token):
    headers = {'token': token}
    resp = get(settings.LIST_AVAILABLIE_WAREHOUSE_URL, headers=headers)
    if resp and resp['result'] is not None:
        return [transfer_warehouse(_)
                for _ in resp['result']['available_warehouses']]
    else:
        return None


def get_all_user_warehouse():
    ''' 获取所有用仓用户，计算仓储费 '''
    resp = get(settings.GET_ALL_USER_WAREHOUSES)
    if resp and resp['result'] is not None:
        return [transfer_user_warehouse(_) for _ in resp['result']]
    else:
        return None


def list_own_warehouse(token):
    headers = {'token': token}
    resp = get(settings.LIST_AVAILABLIE_WAREHOUSE_URL, headers=headers)
    if resp and resp['result'] is not None:
        return [transfer_warehouse(_)
                for _ in resp['result']['available_warehouses']]
    else:
        return None


def transfer_user_warehouse(user_warehouse_dict):
    if not user_warehouse_dict:
        return {}
    user_warehouse = {
        'id': user_warehouse_dict['id'],
        'user_id': user_warehouse_dict['user_id'],
        'warehouse': transfer_warehouse(user_warehouse_dict['warehouse'])
    }
    return user_warehouse


def transfer_warehouse(warehouse_dict):
    if not warehouse_dict:
        return {}
    warehouse = {
        "warehouse_id": warehouse_dict['id'],
        'owner_id': warehouse_dict.get('owner_id'),
        "warehouse_name": warehouse_dict['warehouse_name'],
        "warehouse_code": warehouse_dict['warehouse_code'],
        "warehouse_province": warehouse_dict['province'],
        "warehouse_city": warehouse_dict['city'],
        "warehouse_area": warehouse_dict['area'],
        "warehouse_detail": warehouse_dict['address'],
        'warehouse_longitude': warehouse_dict['longitude'],
        'warehouse_latitude': warehouse_dict['latitude'],
        "warehouse_contact_person": warehouse_dict['contact_person'],
        'warehouse_contact_phone': warehouse_dict['contact_phone'],
        'warehouse_recipient_name': warehouse_dict['recipient_name'],
        'warehouse_recipient_contact': warehouse_dict['recipient_contact'],
        'express': warehouse_dict.get('express', []),
        'service': warehouse_dict.get('service', [])
    }
    return warehouse
