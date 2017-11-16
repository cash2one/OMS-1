# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_api.views import order_view

urlpatterns = [
    url(r'add/$', order_view.add, name='add'),
    url(r'set_mark/$', order_view.set_mark, name='set_mark'),
    url(r'get_detail/$', order_view.get_detail, name='get_detail'),
    url(r'find_order/$', order_view.find_order, name='find_order'),
    url(r'set_status_ori/$', order_view.set_status_ori, name='set_status_ori'),
    url(r'set_status/$', order_view.set_status, name='set_status'),
    url(r'add_skus/$', order_view.add_skus, name='add_skus'),
    url(r'split_order/$', order_view.split_order, name='split_order'),
    url(r'set_warehouse/$', order_view.set_warehouse, name='set_warehouse'),
    url(r'lock_inventory/$', order_view.lock_inventory, name='lock_inventory'),
]
