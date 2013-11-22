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
    url(r'^login/', "django.contrib.auth.views.login"),
    url(r'^register/', "BuLiTippApp.views.register"),
    url(r'^logout/', "BuLiTippApp.views.logout"),

    # Account management
    url(r'^account/$', "BuLiTippApp.views.account"),
    url(r'^account/delete/$', "BuLiTippApp.views.delete_account"),
    
    # Change password functionality
    url(r'^pwchange/', "BuLiTippApp.views.change_pw"),
    url(r'^pwchangedone/', "BuLiTippApp.views.change_pw_done"),

    url(r'^BuLiTipp/$', 'BuLiTippApp.views.index'),
    url(r'^BuLiTipp/(?P<spielzeit_id>\d+)/$', 'BuLiTippApp.views.index'),
    url(r'^BuLiTipp/news/$', 'BuLiTippApp.views.news'),
    url(r'^BuLiTipp/kommi/$', 'BuLiTippApp.views.post_kommentar'),
    url(r'^BuLiTipp/kommi/delete/$', 'BuLiTippApp.views.delete_kommentar'),
    url(r'^BuLiTipp/best/$', 'BuLiTippApp.views.best'),
    url(r'^BuLiTipp/sp(?P<spieltag_id>\d+)/$', 'BuLiTippApp.views.detail'),
    url(r'^BuLiTipp/sp(?P<spieltag_id>\d+)/tipp/$', 'BuLiTippApp.views.tippen'),
    url(r'^BuLiTipp/stat/user/(?P<spielzeit_id>\d+)/$', 'BuLiTippApp.views.user_site'),
    url(r'^BuLiTipp/stat/user/$', 'BuLiTippApp.views.user_site'),

    url(r'^BuLiTipp/saisontipp/(?P<spielzeit_id>\d+)/$', 'BuLiTippApp.views.saisontipp'),
    url(r'^BuLiTipp/saisontipp/$', 'BuLiTippApp.views.saisontipp'),

)
