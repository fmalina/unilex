'''Export a vocabulary as SKOS in RDF/XML format.'''

from django.template import Template, Context

VOCAB_TEMPLATE = Template('''
    <skos:ConceptScheme rdf:nodeID="{{vocab.node_id}}">
        <skos:prefLabel>{{vocab.title}}</skos:prefLabel>
        <skos:definition>{{vocab.description}}</skos:definition>
        <zthes:thesNote label="globallyUniqueId">{{ vocab.node_id }}</zthes:thesNote>
        <zthes:thesNote label="version">{{vocab.version}}</zthes:thesNote>
        <zthes:thesNote label="authority">{{vocab.authority}}</zthes:thesNote>
        <dc:language>{{vocab.language}}</dc:language>
        <dc:date>{{vocab.created_at|date:"d-m-Y"}}</dc:date>
    </skos:ConceptScheme>
''')

CONCEPT_TEMPLATE = Template('''
    <skos:Concept rdf:nodeID="{{ concept.node_id }}">
        <skos:inScheme rdf:nodeID="{{ concept.vocabulary.node_id }}"/>
        <zthes:termNote label="globallyUniqueId">{{ concept.node_id }}</zthes:termNote>
        <skos:prefLabel>{{ concept.name }}</skos:prefLabel>{% if not concept.mother %}
        <skos:topConceptOf rdf:nodeID="{{ concept.vocabulary.node_id }}"/>{% else %}{% for parent in concept.parent.all %}
        <skos:broader rdf:nodeID="{{parent.node_id}}"/>
        {% endfor %}{% endif %}
        {% for child in concept.get_children %}<skos:narrower rdf:nodeID="{{ child.node_id }}"/>
        {% endfor %}{% for rel in concept.related.all %}
        <zthes:termNote identifier="{{ rel.node_id }}" label="category" vocab="{{ rel.vocabulary.node_id }}">{{rel.name}}</zthes:termNote>
        {% endfor %}{% if concept.query %}
        <zthes:termNote label="query">{{ concept.query }}</zthes:termNote>{% endif %}
    </skos:Concept>
''')

def vocab_to_skos(vocab):
    return VOCAB_TEMPLATE.render(Context({'vocab': vocab}))

def concept_to_skos(concept):
    return CONCEPT_TEMPLATE.render(Context({'concept': concept}))

def export_skos(vocab):
    '''A generator to output a SKOS file for vocab piecewise.

    Using a generator allows the WSGI machinery to transfer the document
    without buffering the whole file in memory.
    '''
    yield '<?xml version="1.0" encoding="UTF-8"?>\n'
    yield '<rdf:RDF xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:skos="http://www.w3.org/2004/02/skos/core#" xmlns:zthes="http://www.zthes.org/">\n'
    yield vocab_to_skos(vocab) 

    for concept in vocab.concept_set.all():
        yield concept_to_skos(concept)
    yield '</rdf:RDF>'