from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'BuLiTippApp.views.home', name='home'),
    # url(r'^BuLiTipp/', include('BuLiTipp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', "BuLiTippApp.views.login"),
    url(r'^register/', "BuLiTippApp.views.register"),
    url(r'^logout/', "BuLiTippApp.views.logout"),

    url(r'^BuLiTipp/$', 'BuLiTippApp.views.index'),
	url(r'^BuLiTipp/kommi/$', 'BuLiTippApp.views.post_kommentar'),
	url(r'^BuLiTipp/kommi/delete/$', 'BuLiTippApp.views.delete_kommentar'),
    url(r'^BuLiTipp/best/$', 'BuLiTippApp.views.best'),
    url(r'^BuLiTipp/(?P<spieltag_id>\d+)/$', 'BuLiTippApp.views.detail'),
    url(r'^BuLiTipp/(?P<spieltag_id>\d+)/tipp/$', 'BuLiTippApp.views.tippen'),

)
