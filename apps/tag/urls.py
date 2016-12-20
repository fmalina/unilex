from django.conf.urls import url
from tag.views import about, tag, records, record_json, query

urlpatterns = [
    url(r'^about$', about, name="about"),
    url(r'^(?P<node_id>\d+)', tag, name="tag"),
    url(r'^records$', records, name="records"),
    url(r'^json/(?P<record_id>\d+)$', record_json, name="record_json"),
    url(r'^query$', query, name="query"),
]
