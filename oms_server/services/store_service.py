# -*- coding: UTF-8 -*-
import datetime
from django.core.paginator import Paginator
from django.db import transaction
from oms.models.store import Store
from oms.models.plat import Plat
from oms.services.id_generation_service import IdGenerationService
from oms.extension.exception import CustomException


# 店铺服务
class StoreService:

    @transaction.atomic
    def create(self, user_id, param=None):
        store = Store(
            username=param['username'],
            store_key=param.get('store_key'),
            store_name=param['store_name'],
            address=param.get('address'),
            app_key=param.get('app_key'),
            app_secret=param.get('app_secret'),
            access_token=param.get('access_token'),
            contact_number=param.get('contact_number'),
            refresh_token=param['refresh_token'],
            abbreviation=param.get('abbreviation'),
            platform_id=param['platform_id'],
            auto_merge=param.get('auto_merge', False),
            auto_check=param.get('auto_check', False),
            is_enabled=param.get('is_enabled', True),
            user_id=user_id,
            id=IdGenerationService.generate_store_id(user_id)
        )
        # is_exist = False
        # if param.get('store_key'):
        #     is_exist = Store.objects.\
        #         filter(store_key=param['store_key'],
        #                app_key=param['app_key']).\
        #         count()
        # else:
        #     is_exist = Store.objects.\
        #         filter(app_key=param['app_key']).\
        #         count()
        # if is_exist:
        #     raise Exception('重复密钥创建')
        platform = Plat.objects.get(id=param['platform_id'])
        store.platform_name = platform.name
        store.platform_id = platform.id
        if param.get('access_token_expire_time'):
            access_token_expire_time = datetime.datetime.\
                fromtimestamp(int(param.get('access_token_expire_time')))
            store.access_token_expire_time = access_token_expire_time
        if param.get('refresh_token_expire_time'):
            refresh_token_expire_time = datetime.datetime.\
                fromtimestamp(int(param.get('refresh_token_expire_time')))
            store.refresh_token_expire_time = refresh_token_expire_time
        fetch_order_lastest = datetime.datetime.now() -\
            datetime.timedelta(days=30)
        store.fetch_order_latest = fetch_order_lastest
        store.save()
        self.check_invalid(store)
        return store

    @transaction.atomic
    def update(self, user_id, store_id, data):
        update_fields = ['store_name', 'platform_id', 'app_key', 'app_secret',
                         'access_token', 'refresh_token', 'auto_check', 'auto_merge',
                         'is_enabled', 'username', 'address', 'abbreviation',
                         'access_token', 'refresh_token', 'contact_number']
        store = Store.objects.\
            get(id=store_id, user_id=user_id, is_deleted=False)
        for key in data.keys():
            if key in update_fields:
                setattr(store, key, data[key])
        if data.get('access_token_expire_time'):
            access_token_expire_time = datetime.datetime.\
                fromtimestamp(int(data.get('access_token_expire_time')))
            store.access_token_expire_time = access_token_expire_time
        if data.get('refresh_token_expire_time'):
            refresh_token_expire_time = datetime.datetime.\
                fromtimestamp(int(data.get('refresh_token_expire_time')))
            store.refresh_token_expire_time = refresh_token_expire_time
        if data.get('platform_id'):
            platform = Plat.objects.get(id=data['platform_id'])
            store.platform_name = platform.name
        store.save()
        self.check_invalid(store)
        return store

    def check_invalid(self, store):
        ''' 检查店铺配置 '''
        if not store.app_key or not store.app_secret:
            raise CustomException(40009, 'app key 或 app seceret不存在')
        if store.platform.need_store_key and not store.store_key:
            raise CustomException(40010, 'store key不存在')

    # 店铺列表
    def list(self, user_id, page_size=10, param=None):
        stores = Store.objects.\
            filter(user_id=user_id,
                   is_deleted=False)
        paginator = Paginator(stores, page_size)
        return paginator

    def get(self, user_id, store_id):
        store = Store.objects.\
            get(id=store_id,
                user_id=user_id,
                is_deleted=False)
        return store

    def delete(self, user_id, store_id):
        store = Store.objects.\
            get(user_id=user_id, id=store_id, is_deleted=False)
        store.is_deleted = True
        store.is_enabled = False
        store.save()
        return store
