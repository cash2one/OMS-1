# -*- coding: utf-8 -*-
import jwt
import time
import threading
from rest_framework import serializers
from oms.models.sku import Sku
from oms.models.store import Store
from oms.models.sku_warehouse import SkuWarehouse
from oms.extension.exception import CustomException
from oms_server.services.platforms import interface
from oms_server.services.platforms import common_params

# key = 'xiaobm'
#
#
# # False:token过期, None：token无效
# def jwt_token_certify(token, key='xiaobm'):
#     try:
#         data = jwt.decode(token, key, algorithms=['HS256'])
#         if data:
#             if 'u' in data and 't' in data:
#                 if time.time() < data['t']:
#                     return data
#                 else:
#                     return False
#         return None
#     except BaseException:
#         return None


class SkuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sku
        fields = '__all__'


class SkuService(object):

    @classmethod
    def create(cls, sku_form):
        if 'user_id' not in sku_form:
            raise CustomException('10001', '用户不存在')
        owner = sku_form['user_id']
        sku_form.pop('user_id')
        sku = Sku(**sku_form)
        sku.user_id = owner
        sku.save()
        return None

    @classmethod
    def get(cls, id):
        sku = Sku.objects.get(id=id)
        serializer = SkuSerializer(sku)
        return serializer.data

    @classmethod
    def get_item_code(cls, user_id, item_code):
        try:
            sku = Sku.objects.get(user_id=user_id, item_code=item_code)
            serializer = SkuSerializer(sku)
            return serializer.data
        except Exception as e:
            raise CustomException('10004', '商品不存在')

    @classmethod
    def list_all(cls):
        sku_list = Sku.objects.all()
        serializer = SkuSerializer(sku_list, many=True)
        return serializer.data

    @classmethod
    def lock_count(cls, data):
        item_code = data['item_code']
        user_id = data['user_id']
        count = int(data['quantity'])
        warehouse_id = data['warehouse_id']

        try:
            sku = Sku.objects.get(user_id=user_id, item_code=item_code)
            if warehouse_id == '0':
                sku.available_quantity -= count
                sku.save()
            else:
                sku_warehouse = SkuWarehouse.objects.get(
                    warehouse_id=warehouse_id, sku=sku)
                sku_warehouse.available_quantity -= count
                sku_warehouse.save()
            return True
        except Exception as e:
            print(e)
            raise CustomException('10007', '库存不存在')

    @classmethod
    def update(cls, request):
        result = {'success': False, 'error_code': '10003'}
        token = request.META.get('HTTP_TOKEN')
        if token:
            token_json = jwt_token_certify(token)
            if token_json and isinstance(token_json, dict):
                user_id = token_json['u']
                request_data = request.data
                if 'store_id' in request_data:
                    store_id = request_data['store_id']
                    store = None
                    try:
                        store = Store.objects.get(id=store_id)
                    except BaseException:
                        raise CustomException('10003', '店铺不存在')
                    store_account = {
                        'app_key': store.app_key,
                        'app_secret': store.app_secret,
                        'store_key': store.store_key,
                        'access_token': store.access_token}
                    goods_num = interface.get_product_total(
                        store.platform_name, store_account)
                    pages = common_params.get_pages(goods_num)
                    index = 1
                    for i in range(pages):
                        pageno = i + 1
                        product_page = interface.get_product_list(
                            store.platform_name, store_account, pageno)
                        for product in product_page:
                            oms_goods = interface.to_oms_sku(
                                store.platform_name, user_id, product)
                            sku = Sku(**oms_goods)
                            sku.save()
                            print(
                                "index = %s, 商品标识 = %s, 商品编号 = %s" %
                                (index, oms_goods["item_code"], oms_goods["sku_name"]))
                            index += 1
                    # 返回的结果
                    result_data = {
                        'user_id': user_id,
                        'store_id': store_id,
                        'goods_num': goods_num
                    }
                    # thread_goods = GoodsThread(platform, goods_num, store_account)
                    # thread_goods.start()
                    return result_data
                else:
                    raise CustomException('10003', '店铺不存在')
            elif token_json is None:
                raise CustomException('10012', 'token不存在')
            elif token_json is False:
                raise CustomException('10011', 'token 认证失败')
        else:
            raise CustomException('10010', 'token不存在')
        return result


# class GoodsThread(threading.Thread):
#     def __init__(self, platform_obj, goods_num, store_account):
#         threading.Thread.__init__(self)
#         self.platform_obj = platform_obj
#         self.goods_num = goods_num
#         self.store_account = store_account
#
#     def run(self):
#         pass
