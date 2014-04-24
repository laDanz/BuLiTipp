#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from views import NewsPageView, HomePageView, SpieltagView, SpieltagPrintView, SaisontippView
from views import BestenlisteView, ImpressumView

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
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/print/$', SpieltagPrintView.as_view(), name='spieltag_print'),
	url(r'^spieltag/(?P<spielzeit_id>\s*)(?P<spieltag_id>\s*)$', SpieltagView.as_view(), name='spieltag'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\s*)$', SpieltagView.as_view(), name='spieltag'),
	url(r'^bestenliste/$', BestenlisteView.as_view(), name='bestenliste'),
	url(r'^user$', 'BuLiTippApp.views.userform', name='user'),
	url(r'^impressum$', ImpressumView.as_view(), name='impressum'),
	url(r'^login$', "django.contrib.auth.views.login", name='login'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/tipp/$', 'BuLiTippApp.views.tippen', name='tipp'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/postk/$', 'BuLiTippApp.views.post_kommentar', name='postk'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/delk/$', 'BuLiTippApp.views.delete_kommentar', name='delk'),
	url(r'^register/', "BuLiTippApp.views.register", name="register"),
	url(r'^saisontipp/(?P<spielzeit_id>\d?)/$', SaisontippView.as_view(), name='saisontipp'),
	url(r'^saisontipp/(?P<spielzeit_id>\d+)/post/$', 'BuLiTippApp.views.saisontipp', name='saisontipp_post'),
)
