# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import store_view

urlpatterns = [
    # Examples:
    url(r'^$', store_view.create_or_list, name='create_or_list'),
    url(r'^(?P<pk>\w+)/$', store_view.get_or_update, name='get_or_update'),
    # url(r'^list/$', store_view.list, name='list_stores'),
    url(r'^(?P<pk>\w+)/delete/$', store_view.delete, name='delete_store'),
    # url(r'^update/(?P<pk>\w+)/$', store_view.update, name='update_store'),
]
