from django.conf.urls import url
from oms_api.views import open_interface

urlpatterns = [
    url(r'service$', open_interface.open_interface, name='wms interface entry'),
    url(r'test$', open_interface.test, name='test'),
    url(r'post$', open_interface.posttest, name='post'),
]
