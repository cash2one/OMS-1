# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import deposit_view

urlpatterns = [
    # Examples:
    url(r'^$', deposit_view.deposit, name='balance'),
    url(r'^details$', deposit_view.details, name='details'),
    url(r'^statistic$', deposit_view.statistic, name='statistic'),
    url(r'^charge$', deposit_view.charge, name='charge'),
    url(r'^withdraw$', deposit_view.withdraw, name='withdraw'),
]
