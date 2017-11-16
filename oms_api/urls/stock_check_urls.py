from django.conf.urls import url
from oms_api.views import stock_check_view


urlpatterns = [
    url(r'^stock_check$', stock_check_view.stock_check, name='stock_check'),
]
