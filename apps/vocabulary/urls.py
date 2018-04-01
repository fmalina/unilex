from django.urls import path, re_path
from vocabulary.views import *

urlpatterns = [
    path('', listings, name='listings'),
    path('add', vocabulary_add, name='add'),
    path('autocomplete', autocomplete, name='autocomplete'),
    path('search', search, name='search'),
    path('load-<slug:format>', load_vocab, name='load'),

    path('<slug:vocab_node_id>/',         detail, name='vocabulary'),
    path('<slug:vocab_node_id>/edit',     vocabulary_edit),
    path('<slug:vocab_node_id>/delete',   vocabulary_delete),
    path('<slug:vocab_node_id>/json',     json, name='json'),
    path('<slug:vocab_node_id>/csv',      csv, name='csv'),
    path('<slug:vocab_node_id>/skos',     skos, name='skos'),
    path('<slug:vocab_node_id>/order',    ul, {'style': 'order'}, name='order'),
    path('<slug:vocab_node_id>/nav',      ul, {'style': 'nav'}, name='nav'),
    path('<slug:vocab_node_id>/ul',       ul, {'style': 'ul'}, name='ul'),
    path('<slug:vocab_node_id>/ordering', ordering, name='ordering'),
    path('<slug:vocab_node_id>/new',      concept_new),

    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/new',    concept_new),
    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/edit',   concept_edit),
    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/adopt',  concept_adopt),
    re_path(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/delete', concept_delete),
]
