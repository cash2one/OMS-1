# -*- coding: utf-8 -*-
from django.conf.urls import url
from collaboration.views import order_view

urlpatterns = [
    url(r'^$', order_view.list, name='list'),
    url(r'^(?P<pk>\w+)/$', order_view.get_or_update, name='get_or_update'),
    url(r'^(?P<pk>\w+)/approve$', order_view.check_order, name='check'),
    url(r'^(?P<pk>\w+)/lock$', order_view.lock_order, name='lock'),
    url(r'^(?P<pk>\w+)/unlock$', order_view.unlock_order, name='unlock'),
    # url(r'^(?P<pk>\w+)/withdraw$', order_view.withdraw_order, name='withdraw'),
    # url(r'^(?P<pk>\w+)/delete$', order_view.delete_order, name='delete'),
]
