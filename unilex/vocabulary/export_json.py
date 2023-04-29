from django.utils.html import escape
from unilex.vocabulary.models import Concept


def concept_to_dict(concept, children_lookup, depth, max_depth):
    d = {
        'id': concept.node_id,
        'name': escape(concept.name),
        'url': concept.get_absolute_url(),
        'children': [],
        'data': {'type': 'concept'}
    }
    if concept.description:
        d['description'] = escape(concept.description)
    if concept.query:
        d['data']['query'] = escape(concept.query)
    if not concept.active:
        d['data']['active'] = concept.active
    if depth < max_depth or max_depth == 0:
        children = children_lookup.get(concept.id, [])
        if children:
            depth += 1
        else:
            depth -= 1
        d['children'] = [concept_to_dict(child, children_lookup, depth, max_depth)
                         for child in children]
        d['data']['depth'] = depth
    return d


def vocab_to_dict(vocab, max_depth=0):
    vocab_concepts = {c.id: c for c in vocab.concept_set.all()}
    parent_rels = Concept.parent.through.objects.filter(
        from_concept__vocabulary=vocab)
    children_lookup = {}
    for rel in parent_rels:
        child = vocab_concepts[rel.from_concept_id]
        # create a list of children for each parent ID (to_concept_id)
        children_lookup.setdefault(rel.to_concept_id, []).append(child)

    children = vocab.concept_set.filter(parent__isnull=True)
    # prepending 'v', vocabulary ID cannot match any concept id on the same page
    vocabulary_id = f'v-{vocab.node_id}'
    return {
        'id': vocabulary_id,
        'name': escape(vocab.title),
        'url': vocab.get_absolute_url(),
        'queries': vocab.queries,
        'description': escape(vocab.description),
        'children': [concept_to_dict(child, children_lookup, depth=1, max_depth=max_depth)
                     for child in children],
        'data': {'type': 'vocab'}
    }
