# -*- coding: utf-8 -*-
import logging
# from django.views.decorators.cache import cache_control
# from django.forms import ModelForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import serializers
# from django.views.decorators.csrf import csrf_exempt
from oms.models.store import Store
from oms.models.plat import Plat
from oms_server.services.platforms import interface
from oms_server.services.platforms import common_params
from datetime import datetime
import time


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class StoreService(object):

    @classmethod
    def create(cls, store_form):
        try:
            if 'user_id' not in store_form:
                return {'error_code': '10001', 'success': False}
            if 'plat_id' not in store_form:
                return {'error_code': '10003', 'success': False}
            # owner = User.objects.get(id=store_form['user_id'])
            owner = store_form['user_id']
            # owner = User.objects.all()[0]
            if not owner:
                return {'error_code': '10001', 'success': False}
            plat = Plat.objects.get(id=store_form['plat_id'])
            # store_form.pop('user_id')
            store_form.pop('plat_id')
            store = Store(**store_form)
            store.user_id = owner
            store.platform = plat
            store.save()
        except Exception as e:
            print(e)
            return {'error_code': '10003', 'success': False}
        return {'success': True}

    @classmethod
    def verify_data(cls, store_form):
        if 'user_id' not in store_form:
            return {'error_code': '10001', 'success': False}
        if 'plat_id' not in store_form:
            return {'error_code': '10003', 'success': False}
        # owner = User.objects.get(id=store_form['user_id'])
        owner = store_form['user_id']
        # owner = User.objects.all()[0]
        if not owner:
            return {'error_code': '10001', 'success': False}
        plat = Plat.objects.get(id=store_form['plat_id'])
        store_form.pop('user_id')
        store_form.pop('plat_id')
        store = Store(**store_form)
        store.user_id = owner
        store.platform = plat
        store.save()
        return True

    @classmethod
    def set_last_get_order_at(cls, id, dt):
        store = Store.objects.get(id=id)
        if not store:
            return {
                'error_code': '10003',
                'success': False,
                'result': {
                    'success': False}}
        store.fetch_order_latest = dt
        # print(dt)
        store.save()
        return {'success': True, 'result': {'success': True}}

    @classmethod
    def list_all(cls):
        store_list = Store.objects.all()
        serializer = StoreSerializer(store_list, many=True)
        return {
            'success': True,
            'result': serializer.data
        }

    @classmethod
    def get_store_numbers(cls):
        return Store.objects.filter(is_enabled=True).count()

    @classmethod
    def get_list(cls, page, page_size):
        store_list = Store.objects.filter(is_enabled=True).order_by('id')
        paginator = Paginator(store_list, page_size)
        try:
            stores = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            stores = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            stores = paginator.page(paginator.num_pages)

        return stores.object_list

    @classmethod
    def list(cls, page, page_size):
        store_list = Store.objects.filter(is_enabled=True).order_by('id')
        paginator = Paginator(store_list, page_size)
        try:
            stores = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            stores = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            stores = paginator.page(paginator.num_pages)

        return stores.object_list

    # @classmethod
    # def get_store_key(cls, user, store_key):
    #     store = Store.objects.filter(user=user).get(store_key=store_key)
    #     return store

    @classmethod
    def get_store_key(cls, user, store_key):
        store = Store.objects.get(user=user, store_key=store_key)
        return store

    @classmethod
    def get(cls, id):
        store = Store.objects.get(id=id)
        store_detail = {
            "app_key": store.app_key,
            "app_secret": store.app_secret,
            "expire_in": store.expire_in,
            "access_token_expire_time": store.access_token_expire_time,
            "refresh_token_expire_time": store.refresh_token_expire_time,
            "store_key": store.store_key,
            "platform_name": store.platform_name
        }

        access_token_expire_time = datetime(2000, 1, 1)
        if store.access_token_expire_time:
            access_token_expire_time = store.access_token_expire_time
        target_time = access_token_expire_time.timestamp()

        span = target_time - time.time()

        if span < common_params.HOUR_1:
            # 即将过期
            access_token = interface.refresh_token(
                store.platform_name, store_detail)
            if access_token:
                store.access_token = store_detail['access_token']
                store.expire_in = store_detail['expire_in']
                expire_time = datetime.now().timestamp() + store.expire_in
                store.access_token_expire_time = datetime.fromtimestamp(
                    expire_time)
                store.save()
        return store

    @classmethod
    def update(cls, store):
        store.save()
        return store
