"""Import SKOS vocabularies (tested only with Lexaurus serialisation)
Use from a command line for bulk imports and in the SKOS upload script view.
"""

import logging
import os
import os.path
from tempfile import NamedTemporaryFile
from xml.etree.ElementTree import ElementTree

from django.contrib import messages
from django.conf import settings

from vocabulary.models import *

logfile = settings.PROJECT_ROOT + 'load_skos.log'
logging.basicConfig(filename=logfile, level=logging.DEBUG)


xmlns = {
    'dc': 'http://purl.org/dc/elements/1.1/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'zthes': 'https://unilexicon.com/'
}

expand_tag = lambda ns, tag: '{%s}%s' % (xmlns[ns], tag)
TAG = lambda ns_colon_tag: expand_tag(*ns_colon_tag.split(':'))
expand_map = lambda tag_map: {TAG(k):v for k,v in tag_map.items()}

VOCAB_TAG_MAP = expand_map({
    'skos:prefLabel': 'title',
    'skos:definition': 'description',
    'dc:title': 'title',
    'dc:language': 'language',
    'dc:date': None,
    'dc:description': 'description',
    'dc:format': None,
    'dc:rights': None,
    'zthes:thesNote': ('label', {
            'authority': None,
            'version': None,
            'globallyUniqueId': None,
            'ownersId': None,
            'category': None,
            'rightsHolder': None,
        }
    ),
})

CONCEPT_TAG_MAP = expand_map({
    'skos:prefLabel': 'name',
    'skos:altLabel': 'synonyms[]',
    'skos:topConceptOf': None, # deduceable from inScheme when no broader
    'skos:inScheme': 'vocabulary',
    'skos:broader': 'parent[]',
    'skos:narrower': 'children[]',
    'skos:definition': 'description',
    'skos:related': 'related[]',
    'dc:title': 'name',
    'dc:source': None, # source
    'dc:creator': None, # creator
    'dc:language': None,
    'zthes:termNoteGloballyUniqueId': None,
    'zthes:termNoteDisplayOrder': 'order',
    'zthes:termNoteSourceAuthority': None, # source
    'zthes:termNote': ('label', {
            'category': 'category[]',
            # these need to go to ConceptAttributes
            'displayOrder': 'order',
            'query': 'query',
            'definition': 'description',
            'parentId': None,
            'originalTid': None,
            'option': None, 
            'weight': None, 
            'globallyUniqueId': None, # Duplicate
            'isoCode': None, # Apparently a blob of junk.
            # These seem like workflow stuff we can ignore for now
            'termModifiedBy': None,  # creator
            'created': None,
            'modified': None,
            'rightsHolder': None,
            'authority': None,
            'termApproval': None,
        }
    ),
})


class XMLFormatError(Exception):
    """A problem importing our dialect of SKOS"""


def load_fields_from_node(node, tag_map):
    """Convert an XML node in a format defined by tag_map to a simple dictionary.
    
    Each key in tag_map is a dictionary of element names in ElementTree's qualified name
    format (ie {namespace}nodeName).
    The values define how that element is mapped to a result key:

    - If the mapping value is a string, the result key is that string.
    - If the mapping value is a string ending in [], the same applies, but multiple values are
      accepted and appended to a list.
    - If the mapping value is None, the XML element is ignored.
    - If the mapping is a two element tuple (attribute, attribute_mapping), then the XML attribute
      named by `attribute` will be looked up and one of the above three rules applied as per the
      attribute_mapping dictionary.
    """
    map = {}
    for child in node:
        try:
            mapped_field = tag_map[child.tag]
        except KeyError:
            raise XMLFormatError("Unknown element found in %s: %s" % (node.tag, child.tag))

        if isinstance(mapped_field, tuple):
            attribute, attribute_mapping = mapped_field
            attribute_value = child.get(attribute)
            try:
                mapped_field = attribute_mapping[attribute_value]
            except KeyError:
                raise XMLFormatError("Unknown %s value found for %s: %s" % (
                    attribute,
                    child.tag,
                    attribute_value
                ))

        if mapped_field is not None:
            value = child.text
            xmlns_nid = TAG('rdf:nodeID')
            if not value:
                # Look for a nodeID corresponding to a blank node
                nodeid = child.get(xmlns_nid)
                if nodeid:
                    value = nodeid

            if not value:
                # Look for an rdf:resource URL
                resource = child.get(TAG('rdf:resource'))
                if resource:
                    value = resource

            if mapped_field.endswith('[]'):
                mapped_field = mapped_field[:-2]
                map.setdefault(mapped_field, []).append(value)
            else:
                if mapped_field in map and map[mapped_field] != value:
                    raise XMLFormatError(
                        "Duplicate value '%s' for field %s in node %s" % (
                            value,
                            mapped_field,
                            node.get(xmlns_nid)
                        )
                    )
                map[mapped_field] = value
    return map


class SKOSLoader(object):
    def __init__(self, request=False, log=False):
        self.request = request
        self.log = log
        self.concepts_relationships = []
    
    def message(self, level, message):
        """Log message to a log file or display in the browser"""
        if self.log:
            logging.log(level, message)
        else:
            messages.add_message(self.request, level, message)
    
    def add_parent_relationship(self, parent, child):
        self.concepts_relationships.append((parent, 'parent of', child))

    def add_related_relationship(self, subject, related):
        self.concepts_relationships.append((subject, 'related to', related))

    def save_relationships(self):
        for subject, predicate, object in self.concepts_relationships:
            try:
                subject = Concept.objects.filter(node_id=subject[1], vocabulary=subject[0])[0]
            except Concept.DoesNotExist as e:
                self.message(20, "No subject Concept matching node_id '%s' in %s" % (subject[1], subject[0]))
                continue
            try:
                object = Concept.objects.filter(node_id=object[1], vocabulary=object[0])[0]
            except Exception as e:
                self.message(20, "problem importing %s no %s: %s → %s " % (object[0], predicate, subject, object[1]))
                continue
            if predicate == 'parent of':
                object.parent.add(subject)
            elif predicate == 'related to':
                subject.related.add(object)
        self.concepts_relationships = []

    def load_skos_vocab(self, fname):
        """Import a vocabulary into the DB from xml file fname in SKOS format"""
        doc = ElementTree()
        goto = '/'
        try:
            doc.parse(fname)
        except IOError:
            # In case I passed in a string, like in the upload script instead of a file object
            f = NamedTemporaryFile(delete=False)
            f.write(fname)
            f.close()
            doc.parse(f.name)
            os.unlink(f.name)
        except TypeError:
            self.message(40, 'Sorry, that wasn\'t a SKOS RDF file.')
            goto = '/vocabularies/load-skos'
            
        if doc.getroot().tag != TAG('rdf:RDF'):
            self.message(40, "We need a SKOS RDF file. Try again.")
            goto = '/vocabularies/load-skos'
        
        for vocab in doc.findall('.//'+TAG('skos:ConceptScheme')):
            vocab = self.load_vocab_instance(vocab)
            goto = vocab.get_absolute_url()

        for concept in doc.findall('.//'+TAG('skos:Concept')):
            self.load_concept_instance(concept)
        
        return goto

    def get_node_id(self, element):
        identifiers = []
        node_id = element.get(TAG('rdf:nodeID'))
        if node_id:
            identifiers.append(node_id)
        node_url = element.get(TAG('rdf:about'))
        if node_url:
            identifiers.append(node_url)
        node_fragment = element.get(TAG('rdf:ID'))
        if node_fragment:
            identifiers.append('#' + node_fragment)
        if not identifiers:
            raise XMLFormatError("No node identifier found for " + element.tag)
        if len(identifiers) > 1:
            raise XMLFormatError("Duplicate identifiers found for %s: %s" % (element.tag, identifiers))
        return identifiers[0]

    def load_vocab_instance(self, vocab):
        """Parse a Vocabulary instance from an ElementTree skos:ConceptScheme node."""
        vocab_dict = {
            'node_id': self.get_node_id(vocab) 
        }
        vocab_dict.update(load_fields_from_node(vocab, VOCAB_TAG_MAP))
        # Find or create a Language instance for vocab_dict['language']
        if 'language' in vocab_dict:
            language, created = Language.objects.get_or_create(iso=vocab_dict['language'])
            vocab_dict['language'] = language
        try:
            v = Vocabulary.objects.get(vocab_dict['node_id'])
            v.delete()
        except:
            pass
        v = Vocabulary(**vocab_dict)
        v.user = self.request.user
        v.save()
        return v

    def load_concept_instance(self, node):
        """Parse a Concept instance from an ElementTree skos:Concept node."""
        node_id = self.get_node_id(node)
        concept_dict = {'node_id': node_id}
        concept_dict.update(load_fields_from_node(node, CONCEPT_TAG_MAP))
        vocabulary = concept_dict.pop('vocabulary', None)
        parent     = concept_dict.pop('parent', [])
        related    = concept_dict.pop('related', [])
        category   = concept_dict.pop('category', [])
        children   = concept_dict.pop('children', [])
        synonyms   = concept_dict.pop('synonyms', [])
        try:
            vocabulary = Vocabulary.objects.get(node_id=vocabulary)
        except Vocabulary.DoesNotExist:
            raise XMLFormatError("No Vocabulary with node_id '%s' found for Concept '%s'" % (vocabulary, node_id)) 
        else:
            concept_dict['vocabulary'] = vocabulary
        c = Concept(**concept_dict)
        c.save()
        for s in synonyms:
            c.synonym_set.create(name=s)
        # Queue relationships to be saved once all concepts have been created
        for par in parent:
            self.add_parent_relationship(child=(vocabulary, node_id), parent=(vocabulary, par))
        for child in children:
            self.add_parent_relationship(child=(vocabulary, child), parent=(vocabulary, node_id))
        for rel in related:
            self.add_related_relationship(subject=(vocabulary, node_id), related=(vocabulary, rel))
        for rel in category:
            self.add_related_relationship(subject=(vocabulary, node_id), related=(vocabulary, rel))

    def load_recursive(self, path):
        for subdir, dirs, files in os.walk(path, followlinks=True):
            for file in files:
                if file.endswith('.xml') or file.endswith('.rdf'):
                    file_path = os.path.join(subdir, file)
                    try:
                        self.load_skos_vocab(file_path) 
                    except XMLFormatError:
                        continue
