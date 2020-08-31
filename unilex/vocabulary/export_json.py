def concept_to_dict(concept, depth, max_depth):
    d = {
        'id': concept.node_id,
        'name': concept.name,
        'children': [],
        'data': {'type': 'concept'}
    }
    if concept.description:
        d['description'] = concept.description
    if concept.query:
        d['data']['query'] = concept.query
    if not concept.active:
        d['data']['active'] = concept.active
    if depth < max_depth or max_depth == 0:
        children = concept.get_children()
        if children:
            depth += 1
        else:
            depth -= 1
        d['children'] = [concept_to_dict(child, depth, max_depth)
                         for child in children]
        d['data']['depth'] = depth
    return d


def vocab_to_dict(vocab, max_depth=0):
    children = vocab.concept_set.filter(parent__isnull=True)
    # prepending 'v', vocabulary ID cannot match any concept id on the same page
    vocabulary_id = f'v-{vocab.node_id}'
    return {
        'id': vocabulary_id,
        'name': vocab.title,
        'queries': vocab.queries,
        'description': vocab.description,
        'children': [concept_to_dict(child, depth=1, max_depth=max_depth)
                     for child in children],
        'data': {'type': 'vocab'}
    }
