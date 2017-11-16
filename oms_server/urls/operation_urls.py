# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import operation_view

urlpatterns = [

    url(r'^shared$', operation_view.shared_warehouse_info, name='shared'),
    url(r'^used$', operation_view.used_warehouse_info, name='used'),
]
