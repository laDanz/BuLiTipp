#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from views import NewsPageView, HomePageView, SpieltagView
from views import BestenlisteView, UserFormView, ImpressumView, LoginFormView

urlpatterns = patterns('',
	url(r'^$', HomePageView.as_view(), name='home'),
	url(r'^/$', HomePageView.as_view(), name='home'),
	url(r'^news/$', NewsPageView.as_view(), name='news'),
	url(r'^home/$', HomePageView.as_view(), name='home'),
	url(r'^home/(?P<spielzeit_id>\d+)/$', HomePageView.as_view(), name='home'),
	url(r'^home/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/$', HomePageView.as_view(), name='home'),
	url(r'^spieltag/$', SpieltagView.as_view(), name='spieltag'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/$', SpieltagView.as_view(), name='spieltag'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/$', SpieltagView.as_view(), name='spieltag'),
	url(r'^bestenliste/$', BestenlisteView.as_view(), name='bestenliste'),
	url(r'^user$', 'BuLiTippApp.views.userform', name='user'),
	url(r'^impressum$', ImpressumView.as_view(), name='impressum'),
	url(r'^login$', LoginFormView.as_view(), name='login'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/tipp/$', 'BuLiTippApp.views.tippen', name='tipp'),
)
