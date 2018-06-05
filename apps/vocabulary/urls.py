from django.urls import path, re_path
from vocabulary import views as v

urlpatterns = [
    path('', v.listings, name='listings'),
    path('add', v.vocabulary_add, name='add'),
    path('autocomplete', v.autocomplete, name='autocomplete'),
    path('search', v.search, name='search'),
    path('load-<slug:format>', v.load_vocab, name='load'),

    path('<slug:vocab_node_id>/', v.detail, name='vocabulary'),
    path('<slug:vocab_node_id>/edit', v.vocabulary_edit),
    path('<slug:vocab_node_id>/delete', v.vocabulary_delete),
    path('<slug:vocab_node_id>/json', v.json, name='json'),
    path('<slug:vocab_node_id>/csv', v.csv, name='csv'),
    path('<slug:vocab_node_id>/skos', v.skos, name='skos'),
    path('<slug:vocab_node_id>/order', v.ul, {'style': 'order'}, name='order'),
    path('<slug:vocab_node_id>/nav', v.ul, {'style': 'nav'}, name='nav'),
    path('<slug:vocab_node_id>/ul', v.ul, {'style': 'ul'}, name='ul'),
    path('<slug:vocab_node_id>/ordering', v.ordering, name='ordering'),
    path('<slug:vocab_node_id>/new', v.concept_new),

    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/new', v.concept_new),
    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/edit', v.concept_edit),
    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/adopt', v.concept_adopt),
    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/delete', v.concept_delete),
]
