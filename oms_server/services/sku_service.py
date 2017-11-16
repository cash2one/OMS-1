# -*- coding: utf-8 -*-
import time
import logging
from django.core.paginator import Paginator
from oms.models.sku import Sku
from oms.models.sku_category import SkuCategory
from oms.models.store import Store
from oms_server.services.platforms import interface
from oms_server.services.platforms import common_params
from oms_server.extension.exception import CustomException
from oms.services.id_generation_service import IdGenerationService
from oms_server.tasks import sync_products
from oms_server.services.token_service import TokenService


class SkuService:

    def create(self, user_id, param=None):
        sku = Sku(
            sku_name=param['sku_name'],
            specification=param['specification'],
            bar_code=param['bar_code'],
            item_code=param['item_code'],
            price=param['price'],
            unit=param['unit'],
            category_id=param['category_id'],
            user_id=user_id,
            id=IdGenerationService.generate_sku_id(user_id)
        )
        category = SkuCategory.objects.\
            get(id=param['category_id'], is_deleted=False)
        sku.category_name = category.category_name
        sku.save()
        return sku

    def list(self, user_id, category,
             sku_name, bar_code, item_code, page_size):
        query = Sku.objects.\
            filter(is_deleted=False, user_id=user_id).\
            select_related('category')
        # from django.db.models import Q
        # for _ in params:
        #     q = Q()
        #     query = query.filter(Q(**{}))
        if category:
            query = query.filter(category__category_name=category)
        if sku_name:
            query = query.filter(sku_name=sku_name)
        elif bar_code:
            query = query.filter(bar_code=bar_code)
        elif item_code:
            query = query.filter(item_code=item_code)
        return Paginator(query, per_page=page_size)

    def get(self, user_id, sku_id):
        sku = Sku.objects.\
            select_related('category').\
            get(user_id=user_id,
                is_deleted=False,
                id=sku_id)
        return sku

    def update(self, user_id, sku_id, data):
        sku = Sku.objects.\
            get(user_id=user_id, id=sku_id,
                is_deleted=False)
        update_fields = ['sku_name', 'bar_code',
                         'specification', 'price', 'unit']
        for key in data.keys():
            if key in update_fields:
                setattr(sku, key, data[key])
        if 'item_code' in data.keys():
            sku.item_code = data['item_code']
        if 'category_id' in data.keys():
            category = SkuCategory.objects.\
                get(id=data['category_id'],
                    user_id=user_id,
                    is_deleted=False)
            sku.category_id = category.id
            sku.category_name = category.category_name
        sku.save()
        return sku

    def delete(self, user_id, sku_id):
        sku = Sku.objects.get(user_id=user_id, pk=sku_id)
        sku.is_deleted = True
        sku.save()
        return sku

    def sync(self, request):

        token = request.META.get('HTTP_TOKEN')
        user_id = request.user['id']
        if 'store_id' not in request.data:
            raise CustomException(10003)
        store_id = request.data['store_id']
        try:
            store = Store.objects.get(id=store_id)
        except BaseException:
            raise CustomException(10003)

        # 检查token是否有效
        token_valid = True
        if store.access_token is None:
            token_valid = False
        if store.expire_in == 0:
            token_valid = False
        if store.access_token_expire_time is None:
            token_valid = False
        store_detail = {
            "app_key": store.app_key,
            "app_secret": store.app_secret,
            "expire_in": store.expire_in,
            "access_token_expire_time": store.access_token_expire_time,
            "refresh_token_expire_time": store.refresh_token_expire_time,
            "refresh_token": store.refresh_token,
            "store_key": store.store_key,
            "platform_name": store.platform_name,
            "store_name": store.store_name,
            "user_id": store.user_id,
            "id": store.id
        }
        if token_valid is False:
            logging.warning("%s[%s]access_token无效，刷新access_token" % (store.store_name, store.platform.name))
            token_valid = TokenService().refresh_store_token(store)
            logging.info("%s[%s]access_token=%s" % (store.store_name, store.platform.name, store.access_token))

        total_num = 0
        if token_valid:
            store_detail["access_token"] = store.access_token
            end_stamp = time.time()
            # 默认同步3个月的是商品，有些平台不支持时间参数
            start_stamp = end_stamp - common_params.MONTH_1 * 3
            total_num, error_msg = interface.get_ware_total(
                store.platform_name, store_detail, start_stamp, end_stamp)

            if isinstance(error_msg, str):
                logging.error("%s[%s]get_ware_total错误，error:%s" %
                              (store.store_name, store.platform.name, error_msg))

            if total_num:
                sync_products.delay(store_detail, token)

        # pages = params.get_pages(goods_num)
        # index = 0
        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@3")
        # start_time = time.time()
        # for i in range(pages):
        #     pageno = i + 1
        #     print("=====================================")
        #     product_page = interface.get_product_list(
        #         store.platform_name, store_account, pageno)
        #     for product in product_page:
        #         sku_list = interface.to_oms_sku(
        #             store.platform_name, user_id, product)
        #         for item in sku_list:
        #             sku = Sku(**item)
        #             sku_old = Sku.objects.filter(item_code=item['item_code'], user_id=item['user_id'])
        #             if sku_old:
        #                 sku_old.update(**item)
        #             else:
        #                 sku.id = IdGenerationService.generate_sku_id(user_id)
        #                 sku.save()
        #             index += 1
        # end_time = time.time()
        # 返回的结果

        result_data = {
            'user_id': user_id,
            'store_id': store_id,
            'sku_num': total_num
            # 'seconds': end_time-start_time
        }
        return result_data
