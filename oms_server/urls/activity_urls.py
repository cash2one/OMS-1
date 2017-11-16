# -*- coding: utf-8 -*-
from django.conf.urls import url
from oms_server.views import activity_view

urlpatterns = [
    # Examples:
    url(r'^$', activity_view.create_or_list, name='create_or_list'),
    url(r'^(?P<pk>\w+)/$', activity_view.get_or_update, name='get_or_update'),
    url(r'^(?P<pk>\w+)/delete$', activity_view.delete, name='delete'),
    url(r'^(?P<pk>\w+)/toggle$', activity_view.toggle, name='toggle'),
]
