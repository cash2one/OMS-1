# -*- coding: utf-8 -*-
from django.conf.urls import include, url

urlpatterns = [
    url(r'^collaboration/orders/', include('collaboration.urls.order_urls')),
    url(r'^collaboration/stock_in/', include('collaboration.urls.stock_in_urls')),
]

