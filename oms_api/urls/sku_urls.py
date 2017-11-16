# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_api.views import sku_view

urlpatterns = [
    # url(r'^create/$', sku_view.create, name='create'),
    url(r'^list_all/$', sku_view.list_all, name='list'),
    url(r'^get/$', sku_view.get, name='get'),
    url(r'^get_count/$', sku_view.get_count, name='get_count'),
    url(r'^get_item_code/$', sku_view.get_item_code, name='get_item_code'),
    # url(r'^update/$', sku_view.update, name='update'),
    url(r'^lock_count/$', sku_view.lock_count, name='lock_count')
]
