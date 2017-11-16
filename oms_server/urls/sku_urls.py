# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import sku_view

urlpatterns = [
    # Examples:
    url(r'^$', sku_view.create_or_list, name='create_or_list'),
    url(r'^sync/$', sku_view.sync, name='sync'),
    url(r'^(?P<pk>\w+)/$', sku_view.get_or_update, name='get_or_update'),
    url(r'^(?P<pk>\w+)/delete/$', sku_view.delete, name='delete'),
    # url(r'^(?P<pk>\w+)/$', sku_view.update, name='update_sku'),
]
