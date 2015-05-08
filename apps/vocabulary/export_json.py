def concept_to_dict(concept):
    return {
        'id': concept.node_id,
        'name': concept.name,
        'children': [concept_to_dict(child) for child in concept.get_children()],
        'data': {
            'type': 'concept',
            'query': concept.query,
            'active': concept.active
        }
    }

def vocab_to_dict(vocab):
    children = vocab.concept_set.filter(parent__isnull=True)
    vocabulary_id = 'v-%s' % vocab.node_id # prepending 'v', vocabulary ID cannot match any concept id on the same page
    return {
        'id': vocabulary_id,
        'name': vocab.title,
        'queries': vocab.queries,
        'children': [concept_to_dict(child) for child in children],
        'data': {'type': 'vocab'}
    }
