import markdown
from lxml.html import fromstring
from unilex.vocabulary.models import Vocabulary, Concept


def load_md(user, md_file, title):
    s = md_file.decode().replace('::', ':').replace('**', '')
    html = markdown.markdown(s)
    dom = fromstring(html)
    vocab_el = dom.cssselect("ul")[0]
    l1_title = vocab_el.cssselect("li:nth-child(1)")
    if len(l1_title) == 1:
        title = l1_title[0].text
    v = Vocabulary.objects.create(user=user, title=title)
    parents = []
    for li in vocab_el.cssselect("li"):
        depth = (len(list(li.iterancestors())) - 3) // 2
        name = li.text.strip()
        desc = ''
        if ':' in name:
            name, desc = name.split(':')
            name = name.strip()
            desc = desc.strip().replace('\n', '')
        # Pop items off the stack until we reach the correct depth
        while len(parents) > depth:
            parents.pop()
        concept = Concept.objects.create(
            vocabulary=v, name=name, description=desc)
        if parents:
            concept.parent.add(parents[-1])
            concept.save()
        parents.append(concept)
    return v
