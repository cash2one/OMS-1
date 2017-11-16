# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import shared_warehouse_view

urlpatterns = [
    url(r'^delivery_orders$', shared_warehouse_view.delivery_orders, name='delivery_orders'),
    url(r'^entry_orders$', shared_warehouse_view.entry_orders, name='entry_orders'),
    url(r'^inventory$', shared_warehouse_view.inventory, name='inventory'),
]
