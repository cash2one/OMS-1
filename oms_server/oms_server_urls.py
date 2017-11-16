# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from oms_server.views import api_view

urlpatterns = [
    # Examples:
    url(r'^api/$', api_view.api, name='api'),
    url(r'^api/platforms/', include('oms_server.urls.platform_urls')),
    url(r'^api/stores/', include('oms_server.urls.store_urls')),
    url(r'^api/skus/', include('oms_server.urls.sku_urls')),
    url(r'^api/inventory/', include('oms_server.urls.inventory_urls')),
    url(r'^api/activities/', include('oms_server.urls.activity_urls')),
    url(r'^api/orders/', include('oms_server.urls.order_urls')),
    url(r'^api/sku_categories/', include('oms_server.urls.sku_category_urls')),
    url(r'^api/stock_in/', include('oms_server.urls.stock_in_urls')),
    url(r'^api/cmm/', include('oms_server.urls.cmm_urls')),
    url(r'^api/cop/', include('oms_server.urls.cop_urls')),
    url(r'^api/bill/', include('oms_server.urls.bill_urls')),
    url(r'^api/receipt/', include('oms_server.urls.receipt_urls')),
    url(r'^api/balance/', include('oms_server.urls.balance_urls')),
    url(r'^api/wallet/', include('oms_server.urls.pay_urls')),
    url(r'^api/deposit/', include('oms_server.urls.deposit_urls')),
    url(r'^api/shared/', include('oms_server.urls.shared_warehouse_urls')),
    url(r'^api/operation_info/', include('oms_server.urls.operation_urls')),
]
