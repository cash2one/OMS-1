# -*- coding: utf-8 -*-
from django.conf.urls import include, url


urlpatterns = [
    url(r'^oms/api/order/', include('oms_api.urls.order_urls')),
    url(r'^oms/api/sku/', include('oms_api.urls.sku_urls')),
    url(r'^oms/api/store/', include('oms_api.urls.store_urls')),
    url(r'^oms/api/activity/', include('oms_api.urls.activity_urls')),
    url(r'^oms/open_api/', include('oms_api.urls.cop_urls')),
    url(r'^oms/api/stock_check/', include('oms_api.urls.stock_check_urls')),
]
