# -*- coding: utf-8 -*-
import time
from datetime import datetime
from rest_framework import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from oms.models.store import Store
from oms.models.plat import Plat
from oms.extension.exception import CustomException


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class StoreService(object):

    @classmethod
    def create(cls, store_form):
        try:
            if 'user_id' not in store_form:
                raise CustomException('10001', '用户不存在')
            if 'plat_id' not in store_form:
                raise CustomException('10003', '平台不存在')
            owner = store_form['user_id']
            plat = Plat.objects.get(id=store_form['plat_id'])
            store_form.pop('plat_id')
            store = Store(**store_form)
            store.user_id = owner
            store.platform = plat
            store.save()
        except Exception as e:
            print(e)
            raise CustomException('10003', '平台不存在')
        return None

    @classmethod
    def verify_data(cls, store_form):
        if 'user_id' not in store_form:
            raise CustomException('10001', '用户不存在')
        if 'plat_id' not in store_form:
            raise CustomException('10003', '平台不存在')
        owner = store_form['user_id']
        try:
            plat = Plat.objects.get(id=store_form['plat_id'])
            store_form.pop('user_id')
            store_form.pop('plat_id')
            store = Store(**store_form)
            store.user_id = owner
            store.platform = plat
            store.save()
        except Exception as e:
            raise CustomException('10003', '平台不存在')
        return True

    @classmethod
    def set_last_get_order_at(cls, id, dt):
        store = Store.objects.get(id=id)
        store.fetch_order_latest = dt
        store.save()
        return {'success': True}

    @classmethod
    def list_all(cls):
        store_list = Store.objects.all()
        serializer = StoreSerializer(store_list, many=True)
        return serializer.data

    @classmethod
    def get_store_numbers(cls):
        return Store.objects.filter(is_enabled=True, is_deleted=False).count()

    @classmethod
    def get_list(cls, page, page_size):
        store_list = Store.objects.\
            filter(is_enabled=True, is_deleted=False).order_by('id')
        paginator = Paginator(store_list, page_size)
        try:
            stores = paginator.page(page)
        except PageNotAnInteger:
            stores = paginator.page(1)
        except EmptyPage:
            stores = paginator.page(paginator.num_pages)
        return stores.object_list

    @classmethod
    def list(cls, page, page_size):
        store_list = Store.objects.filter(is_enabled=True).order_by('id')
        paginator = Paginator(store_list, page_size)
        try:
            stores = paginator.page(page)
        except PageNotAnInteger:
            stores = paginator.page(1)
        except EmptyPage:
            stores = paginator.page(paginator.num_pages)
        return stores.object_list

    @classmethod
    def get_store_key(cls, user, store_key):
        store = Store.objects.get(user=user, store_key=store_key)
        return store

    @classmethod
    def get(cls, store_id):
        try:
            store = Store.objects.get(id=store_id)
            return store
        except BaseException as e:
            raise CustomException('10012', '店铺不存在')

    @classmethod
    def is_token_valid(cls, store_id):
        try:
            store = Store.objects.get(id=store_id)
            success = True
            if store.access_token is None:
                success = False
            if store.expire_in == 0:
                success = False
            if store.access_token_expire_time is None:
                success = False
        except BaseException as e:
            success = False
        return success
