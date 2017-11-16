# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import receipt_view

urlpatterns = [
    # Examples:
    url(r'^$', receipt_view.receipt, name='receipt'),
    url(r'^statistics$', receipt_view.statistics, name='statistics'),
    url(r'^details$', receipt_view.details, name='details'),
    # url(r'^details$', bill_view.details, name='details'),
    # url(r'^unsettle_statistics$', bill_view.unsettle_statistics, name='unsettle_statistics'),
]
