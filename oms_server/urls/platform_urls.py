# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import platform_view

urlpatterns = [
    url(r'^$', platform_view.create_or_list, name='create_or_list'),
]
