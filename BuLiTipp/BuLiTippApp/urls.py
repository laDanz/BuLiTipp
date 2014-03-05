#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from views import NewsPageView, HomePageView, SpieltagView, SpieltagPrintView
from views import BestenlisteView, ImpressumView

urlpatterns = patterns('',
	url(r'^$', 'BuLiTippApp.views.home'),
	url(r'^/$', 'BuLiTippApp.views.home'),
	url(r'^news/$', NewsPageView.as_view(), name='news'),
	url(r'^home/$', HomePageView.as_view(), name='home'),
	url(r'^home/(?P<spielzeit_id>\d+)/$', HomePageView.as_view(), name='home'),
	url(r'^home/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/$', HomePageView.as_view(), name='home'),
	url(r'^spieltag/$', SpieltagView.as_view(), name='spieltag'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/$', SpieltagView.as_view(), name='spieltag'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/$', SpieltagView.as_view(), name='spieltag'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/print/$', SpieltagPrintView.as_view(), name='spieltag_print'),
	url(r'^spieltag/(?P<spielzeit_id>\s*)(?P<spieltag_id>\s*)$', SpieltagView.as_view(), name='spieltag'),
	url(r'^bestenliste/$', BestenlisteView.as_view(), name='bestenliste'),
	url(r'^user$', 'BuLiTippApp.views.userform', name='user'),
	url(r'^user/changepw$', 'BuLiTippApp.views.change_pw', name='user_pwchange'),
	url(r'^user/delete$', 'BuLiTippApp.views.delete_account', name='user_delete'),
	url(r'^impressum$', ImpressumView.as_view(), name='impressum'),
	url(r'^login$', "django.contrib.auth.views.login", name='login'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/tipp/$', 'BuLiTippApp.views.tippen', name='tipp'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/postk/$', 'BuLiTippApp.views.post_kommentar', name='postk'),
	url(r'^spieltag/(?P<spielzeit_id>\d+)/(?P<spieltag_id>\d+)/delk/$', 'BuLiTippApp.views.delete_kommentar', name='delk'),
	url(r'^register/', "BuLiTippApp.views.register", name="register"),
	url(r'^tg/new$', 'BuLiTippApp.views.tg_new_form', name='new_tippgemeinschaft'),
	url(r'^tg/(?P<tg_id>\d+)/$', 'BuLiTippApp.views.tg_show_form', name='show_tippgemeinschaft'),
	url(r'^tg/(?P<tg_id>\d+)/invite/new$', 'BuLiTippApp.views.tg_einladung_new_form', name='new_tg_einladung'),
)
