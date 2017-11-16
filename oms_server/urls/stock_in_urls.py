# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import stock_in_view
import logging

urlpatterns = [
    url(r'^$', stock_in_view.create_or_list, name='create_or_list'),
    url(r'^(?P<pk>\w+)/$', stock_in_view.get_or_update, name='get_or_update'),
    url(r'^(?P<pk>\w+)/delete/$', stock_in_view.delete, name='delete'),
    # url(r'^(?P<pk>\w+)/$', sku_view.update, name='update_sku'),
    url(r'^(?P<pk>\w+)/cancle/$', stock_in_view.cancle, name='cancle'),

]
