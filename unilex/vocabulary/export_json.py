from django.utils.html import escape
from unilex.vocabulary.models import Concept


def get_children(concept, vocab_concepts, parent_rels):
    child_pks = [x.from_concept_id for x in parent_rels
                 if x.to_concept_id == concept.pk]
    children = [x for x in vocab_concepts if x.pk in child_pks]
    return children


def concept_to_dict(concept, vocab_concepts, parent_rels, depth, max_depth):
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
        children = get_children(concept, vocab_concepts, parent_rels)
        if children:
            depth += 1
        else:
            depth -= 1
        d['children'] = [concept_to_dict(child, vocab_concepts, parent_rels, depth, max_depth)
                         for child in children]
        d['data']['depth'] = depth
    return d


def vocab_to_dict(vocab, max_depth=0):
    vocab_concepts = list(vocab.concept_set.all())
    pks = [c.pk for c in vocab_concepts]
    parent_rels = list(Concept.parent.through.objects.filter(pk__in=pks))

    children = vocab.concept_set.filter(parent__isnull=True)
    # prepending 'v', vocabulary ID cannot match any concept id on the same page
    vocabulary_id = f'v-{vocab.node_id}'
    return {
        'id': vocabulary_id,
        'name': escape(vocab.title),
        'url': vocab.get_absolute_url(),
        'queries': vocab.queries,
        'description': escape(vocab.description),
        'children': [concept_to_dict(child, vocab_concepts, parent_rels, depth=1, max_depth=max_depth)
                     for child in children],
        'data': {'type': 'vocab'}
    }
