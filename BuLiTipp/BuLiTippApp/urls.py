# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
import BuLiTipp

from BuLiTippApp.views import NewsPageView, SpieltagView

urlpatterns = patterns('',
	url(r'^news/$', NewsPageView.as_view(), name='news'),
	# neue url's
	url(r'^home$', 'BuLiTippApp.views.index'),
	url(r'^spieltag$', SpieltagView.as_view(), name='st'),
	url(r'^bestenliste/$', 'BuLiTippApp.views.best'),
)
