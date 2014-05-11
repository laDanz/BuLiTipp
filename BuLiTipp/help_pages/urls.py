from django.conf.urls.defaults import *

urlpatterns = patterns('',

    #list of all categories
    url(r'^$', 'help_pages.views.category_list', name='help_category_list'),

    #individual item - note place in the urlconf to avoid lookup fail
    url(r'^topic/(?P<cat_identifier>.+)/item/(?P<item_identifier>.+)/$', 'help_pages.views.single_item', name='help_single_item'),

    #list of all items in a particular category - works with integer or slug
    url(r'^topic/(?P<identifier>.+)/$', 'help_pages.views.item_list', name='help_item_list'),

    #all items with a specific tag
    url(r'^tagged/(?P<tag>.+)/$', 'help_pages.views.items_by_tag', name='help_items_by_tag'),

    #search results
    url(r'^search/results/$', 'help_pages.views.search_results', name='help_search_results'),
)