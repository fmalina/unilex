from django.urls import path
from tag.views import about, tag, records, record_json, query

urlpatterns = [
    path('about', about, name="about"),
    path('<int:node_id>', tag, name="tag"),
    path('records', records, name="records"),
    path('json/<int:record_id>', record_json, name="record_json"),
    path('query', query, name="query"),
]
