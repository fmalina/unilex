from django.conf.urls import url
from vocabulary.views import *

urlpatterns = [
    url(r'^$',                        listings, name='listings'),
    url(r'^add$',                     vocabulary_add, name='add'),
    url(r'^autocomplete$',            autocomplete, name='autocomplete'),
    url(r'^search$',                  search),
    url(r'^load-(?P<format>[a-z]+)$', load_vocab, name='load'),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/$',         detail, name='vocabulary'),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/edit$',     vocabulary_edit),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/delete$',   vocabulary_delete),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/json$',     json    , name='json'    ),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/csv$',      csv     , name='csv'     ),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/skos$',     skos    , name='skos'    ),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/order$',    ul, {'style': 'order'}, name='order'),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/nav$',      ul, {'style': 'nav'}, name='nav'),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/ul$',       ul, {'style': 'ul'}, name='ul'),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/ordering$', ordering, name='ordering'),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/new$',      concept_new),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/new',    concept_new),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/edit',   concept_edit),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/adopt',  concept_adopt),
    url(r'^(?P<vocab_node_id>[a-z0-9-_]+)/(?P<node_id>[A-Za-z0-9-: ]+)/delete', concept_delete),
]
