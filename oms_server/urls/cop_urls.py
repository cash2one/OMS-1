# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import cop_view

urlpatterns = [
    # Examples:
    url(r'^$', cop_view.cop, name='cop'),
]
