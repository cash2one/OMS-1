# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import bill_view

urlpatterns = [
    # Examples:
    url(r'^order_express$', bill_view.order_express, name='order_express'),
    url(r'^test$', bill_view.test, name='test'),
    url(r'^test_storge_bill$', bill_view.test_storge_bill, name='test_storge_bill'),
    url(r'^over_bill$', bill_view.test_overdue_bill, name='over_bill'),
    url(r'^$', bill_view.api, name='api'),
    url(r'^statistics$', bill_view.statistics, name='statistics'),
    url(r'^all_statistics$', bill_view.all_statistics, name='all_statistics'),
    url(r'^details$', bill_view.details, name='details'),
    url(r'^pay$', bill_view.pay, name='pay'),
    url(r'^unsettle_statistics$', bill_view.unsettle_statistics, name='unsettle_statistics'),
]
