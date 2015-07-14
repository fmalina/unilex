from django.conf.urls import url, patterns, include
from django.conf import settings

urlpatterns = patterns('tag.views',
    (r'^$', 'nothing'),
    (r'^false$', 'nothing'),
    (r'^about$', 'about'),
    (r'^(?P<node_id>\d+)', 'tag'),
    (r'^query$', 'query'),
    
    (r'^site$', 'site'),
    (r'^autocomplete$', 'autocomplete'),
    (r'^search$', 'search'),
    (r'^(?P<page_id>\d+)$', 'page'),
    (r'^(?P<page_id>\d+)/edit$', 'page_edit'),
)
