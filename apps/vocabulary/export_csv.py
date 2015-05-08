def to_csv(aa):
    str = ''
    for a in aa:
        str = str + a
    return str

def concept_to_csv(concept):
    return '%s"%s"\n%s' % (
        concept.depth_indent(),
        concept.name,
        to_csv([concept_to_csv(child) for child in concept.get_children()])
    )

def export_csv(vocab):
    return to_csv([concept_to_csv(child) for child in vocab.get_children()])
