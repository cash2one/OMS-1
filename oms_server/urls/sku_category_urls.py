# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import sku_category_view

urlpatterns = [
    url(r'^$', sku_category_view.create_or_list, name='create_or_list'),
    url(r'^(?P<pk>\w+)/$', sku_category_view.get_or_update, name='get_or_update'),
    url(r'^(?P<pk>\w+)/delete/$', sku_category_view.delete, name='delete'),
]