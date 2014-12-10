#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from views import ParseView, SyncView, ClearCacheView

urlpatterns = patterns('',
	url(r'^parse/(?P<spieltag_id>\d+)/$', ParseView.as_view(), name='parse'),
	url(r'^sync/(?P<spieltag_id>\d+)/(?P<spiel_id>\d+)/$', SyncView.as_view(), name='sync'),
	url(r'^sync/(?P<spieltag_id>\d+)/$', SyncView.as_view(), name='sync'),
	url(r'^clearcache/(?P<syncresult_id>\d+)/$', ClearCacheView.as_view(), name='clearcache'),
)
