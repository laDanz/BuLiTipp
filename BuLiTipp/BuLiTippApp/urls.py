# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url

from views import NewsPageView

urlpatterns = patterns('',
    url(r'^news/$', NewsPageView.as_view(), name='news'),
)
