def to_csv(aa):
    s = ''
    for a in aa:
        s = s + a
    return s

def concept_to_csv(concept):
    return '%s,%s"%s"\n%s' % (
        concept.node_id,
        concept.depth_indent(),
        concept.name,
        to_csv([concept_to_csv(child) for child in concept.get_children()])
    )

def export_csv(vocab):
    return to_csv([concept_to_csv(child) for child in vocab.get_children()])
