# -*- coding:utf-8 -*-
import requests

from oms.extension.exception import CustomException

AK = 'GUShqxTp75uGvA4WwD7dIjvuYmzd3hbK'
OUT_PUT = 'json'
API_URL_GET_LNG_LAT = 'http://api.map.baidu.com/geocoder/v2/'
API_URL_GET_DISTANCE = 'http://api.map.baidu.com/routematrix/v2/driving'


HEADERS = {'Content-Type': 'application/json;charset=utf-8'}


def get_lng_lat(address):
    try:
        result = requests.\
            get(API_URL_GET_LNG_LAT + '?address=' +
                address + '&output=' + OUT_PUT + '&ak=' + AK).\
            json()
        lat = result['result']['location']['lat']
        lng = result['result']['location']['lng']
        return round(lng, 6), round(lat, 6)
    except Exception as e:
        raise CustomException(60002, '百度地图API获取经纬度失败！')
        return (0, 0)


def get_distance(source, destination):
    ori_lat, ori_lng = get_lng_lat(source)
    origin = ','.join([str(ori_lng), str(ori_lat)])
    des_lat, des_lng = get_lng_lat(destination)
    destination = ','.join([str(des_lng), str(des_lat)])
    print(origin, destination)
    res = requests.\
        get(API_URL_GET_DISTANCE + '?origins=' +
            origin + '&destinations=' +
            destination + '&output=' + OUT_PUT +
            '&ak=' + AK).\
        json()
    if res['status'] == 0:
        distance = res['result'][0]['distance']['value']
        return int(distance)
    else:
        print(res)
        raise CustomException(60003, '百度地图API获取距离失败')


if __name__ == '__main__':
    r = get_distance("北京", "美国")
    print(r)
