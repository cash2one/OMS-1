# -*- coding: utf-8 -*-
from django.conf.urls import include, url


urlpatterns = [
    url(r'^', include('oms_api.oms_api_urls')),
    url(r'^', include('oms_server.oms_server_urls')),
    url(r'^', include('collaboration.collaboration_urls'))
]