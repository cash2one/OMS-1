import requests
from oms.extension.exception import CustomException


HEADERS = {'Content-Type': 'text/json;charset=utf-8'}


def post(url, headers={}, body=None):
    for key in HEADERS:
        headers.setdefault(key, HEADERS[key])
    res = None
    with requests.post(url, headers=headers, data=body) as res:
        res = res
    return res


def get(url, headers={}):
    for key in HEADERS:
        headers.setdefault(key, HEADERS[key])
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise CustomException(60001)
    return res.json()