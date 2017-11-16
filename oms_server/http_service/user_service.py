from django.conf import settings
from oms_server.extension.http_utils import get

# GET_USER_INFO_URL = 'http://47.95.235.167:8002/api/users/'
# GET_ALL_SUB_USERS =\
#     'http://47.95.235.167:8002/api/users/all_sub_users'


# 获取用户详情
def get_user_info(user_id):
    url = settings.GET_USER_INFO_URL + str(user_id)
    resp = get(url)
    if resp and resp['result'] is not None:
        return transfer_user(resp['result'])
    elif not resp['result']:
        return {}
    return None


def get_all_sub_users():
    ''' 获取所有用仓用户 '''
    resp = get(settings.GET_ALL_SUB_USERS)
    if resp and resp['result'] is not None:
        return [transfer_user(_) for _ in resp['result']]
    else:
        return None


def transfer_user(user_dict):
    if 'id' in user_dict:
        user_id = user_dict['id']
    if 'user_id' in user_dict:
        user_id = user_dict['user_id']
    user = {
        'user_id': user_id,
        'nickname': user_dict['nickname'],
        'phone': user_dict['phone']
    }
    return user
