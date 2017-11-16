# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import cmm_view

urlpatterns = [
    # Examples:
    url(r'^warehouses/(?P<warehouse_id>\w+)$', cmm_view.warehouses, name='warehouse'),
    url(r'^available_warehouses/$', cmm_view.available_warehouses, name='available_warehouse'),
]
