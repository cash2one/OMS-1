# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_api.views import store_view

urlpatterns = [
    url(r'get_count/$', store_view.get_store_numbers, name='get_count'),
    url(r'get_list/$', store_view.get_list, name='get_list'),
    url(r'^get/$', store_view.get, name='get'),
    url(r'^set_last_get_order_at/$',
        store_view.set_last_get_order_at,
        name='set_last_get_order_at'),
    # url(r'^create/', store_view.create, name='create'),
    url(r'^list_all/', store_view.list_all, name='list'),
]
