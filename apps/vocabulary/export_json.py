def concept_to_dict(concept):
    d = {
        'id': concept.node_id,
        'name': concept.name,
        'description': concept.description,
        'children': [concept_to_dict(child) for child in concept.get_children()],
        'data': {'type': 'concept'}
    }
    if concept.query:
        d['data']['query'] = concept.query
    if not concept.active:
        d['data']['active'] = concept.active
    return d

def vocab_to_dict(vocab):
    children = vocab.concept_set.filter(parent__isnull=True)
    vocabulary_id = 'v-%s' % vocab.node_id # prepending 'v', vocabulary ID cannot match any concept id on the same page
    return {
        'id': vocabulary_id,
        'name': vocab.title,
        'queries': vocab.queries,
        'description': vocab.description,
        'children': [concept_to_dict(child) for child in children],
        'data': {'type': 'vocab'}
    }
