# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import pay_view

urlpatterns = [
    url(r'^pay$', pay_view.dev_auth_pay, name='pay'),
    url(r'^paid$', pay_view.paid, name='paid'),
]