from vocabulary.models import Vocabulary, Concept
from tag.get import Get

def test_queries():
    vocab = Vocabulary.objects.get(node_id='test')
    concepts = Concept.objects.filter(vocabulary=vocab)
    for c in concepts:
        if c.query:
            sr = Get(c.query).parse()
            print('%s pieces in: %s' % (sr['no_of_records'], c.forward_path()))
            # c.results = sr['no_of_results']
            # c.save()

# test_queries()