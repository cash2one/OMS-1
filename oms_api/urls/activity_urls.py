# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_api.views import activity_view

urlpatterns = [
    url(r'get/$', activity_view.get, name='get'),
]
