from xml.etree.ElementTree import ElementTree as ET
from unilex.vocabulary.load_skos import TAG
from django.conf import settings

ev = settings.PROJECT_ROOT+'archive/eurovoc_skos.rdf'
doc = ET()

# doc.parse(ev)
# for e in doc.iter():
#     print(e)
