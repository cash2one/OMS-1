# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import balance_view

urlpatterns = [
    # Examples:
    url(r'^$', balance_view.balance, name='balance'),
    url(r'^recent$', balance_view.recent, name='recent'),
    url(r'^details$', balance_view.details, name='details'),
    url(r'^charge$', balance_view.charge, name='charge'),
    url(r'^withdraw$', balance_view.withdraw, name='withdraw'),
]
