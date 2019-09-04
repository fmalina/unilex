from django.urls import path
from tag.views import TaggingView, about, records, record_json, query

urlpatterns = [
    path('', TaggingView.as_view(template_name='tag/record.html'), name="add-record"),
    path('about', about, name="about"),
    path('records', records, name="records"),
    path('json/<int:record_id>', record_json, name="record_json"),
    path('query', query, name="query"),
    path('test', TaggingView.as_view(), name="test-record"),
    path('-<path:key>', TaggingView.as_view(), name="tag-record"),
    path('<path:key>', TaggingView.as_view(template_name='tag/record.html'), name="tag"),
]
