# -*- coding: utf-8 -*-
from django.conf.urls import url
from collaboration.views import stock_in_view

urlpatterns = [
    url(r'^$', stock_in_view.list, name='list'),
    url(r'^(?P<pk>\w+)/$', stock_in_view.get_or_update, name='get_or_update'),
    url(r'^(?P<pk>\w+)/delete/$', stock_in_view.delete, name='delete'),
]
