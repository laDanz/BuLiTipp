from django.conf.urls import patterns, include, url

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
# Examples:
url(r'^$', 'BuLiTippApp.views.home'),
url(r'^admin/', include(admin.site.urls)),
url(r'^logout/', "BuLiTippApp.views.logout", name="logout"),

url(r'^BuLiTipp/', include('BuLiTippApp.urls')),
url(r'^sync/', include('KickerSync.urls')),
url(r'^home/', "BuLiTippApp.views.home"),
url(r'^autocomplete/', include('autocomplete_light.urls')),
url(r'^help_pages/', include('help_pages.urls')),
)
