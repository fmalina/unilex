from django.conf.urls import url, patterns, include
from django.conf import settings

urlpatterns = patterns('tag.views',
    url(r'^about$', 'about', name="about"),
    url(r'^(?P<node_id>\d+)', 'tag', name="tag"),
    url(r'^records$', 'records', name="records"),
    url(r'^json/(?P<record_id>\d+)$', 'record_json', name="record_json"),
    url(r'^query$', 'query', name="query"),
)
