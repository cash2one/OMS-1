# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import inventory_view

urlpatterns = [
    url(r'^$', inventory_view.list, name='list'),
]
