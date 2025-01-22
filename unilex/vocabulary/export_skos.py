"""Export a vocabulary as SKOS in RDF/XML format.
"""

from django.template import Template, Context
from unilex.vocabulary.load_skos import xmlns

NAMESPACES = '\n'.join(['xmlns:%s="%s"' % (k,v) for k, v in xmlns.items()])

VOCAB_TEMPLATE = Template('''
<skos:ConceptScheme rdf:nodeID="{{v.node_id}}">
    <skos:prefLabel>{{v.title}}</skos:prefLabel>
    <skos:definition>{{v.description}}</skos:definition>
    {% if v.version %}<zthes:thesNote label="version">{{v.version}}</zthes:thesNote>{% endif %}
    {% if v.authority %}<zthes:thesNote label="authority">{{v.authority.code}}</zthes:thesNote>{% endif %}
    {% if v.language %}<dc:language>{{v.language}}</dc:language>{% endif %}
    <dc:date>{{v.created_at|date:"d-m-Y"}}</dc:date>
</skos:ConceptScheme>
''')

CONCEPT_TEMPLATE = Template('''
<skos:Concept rdf:nodeID="{{ concept.node_id }}">
    <skos:inScheme rdf:nodeID="{{ concept.vocabulary.node_id }}"/>
    <skos:prefLabel>{{ concept.name }}</skos:prefLabel>{% if concept.description %}
    <skos:definition>{{ concept.description }}</skos:definition>{% endif %}
    {% if not concept.mother %}
    <skos:topConceptOf rdf:nodeID="{{ concept.vocabulary.node_id }}"/>
    {% else %}{% for parent in concept.parent.all %}
    <skos:broader rdf:nodeID="{{parent.node_id}}"/>{% endfor %}{% endif %}
    {% for child in concept.get_children %}<skos:narrower rdf:nodeID="{{ child.node_id }}"/>
    {% endfor %}{% for rel in concept.related.all %}
        {% if rel.vocabulary == concept.vocabulary %}
            <skos:related rdf:nodeID="{{rel.node_id}}"/>
        {% else %}
            <zthes:termNote identifier="{{ rel.node_id }}" label="category"
                vocab="{{ rel.vocabulary.node_id }}">{{rel.name}}</zthes:termNote>
        {% endif %}
    {% endfor %}{% if concept.query %}
    <zthes:termNote label="query">{{ concept.query }}</zthes:termNote>{% endif %}
</skos:Concept>
''')


def vocab_to_skos(vocab):
    return VOCAB_TEMPLATE.render(Context({'v': vocab}))


def concept_to_skos(concept):
    return CONCEPT_TEMPLATE.render(Context({'concept': concept}))


def export_skos(vocab):
    """A generator to output a SKOS file for vocab piecewise.

    Using a generator allows the WSGI machinery to transfer the document
    without buffering the whole file in memory.
    """
    yield '<?xml version="1.0" encoding="UTF-8"?>\n'
    yield '<rdf:RDF '+NAMESPACES+'>\n'
    yield vocab_to_skos(vocab) 

    for concept in vocab.concept_set.all():
        yield concept_to_skos(concept)
    yield '</rdf:RDF>'
