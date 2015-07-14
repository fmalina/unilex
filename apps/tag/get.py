from django.contrib import messages
from lxml import etree
import urllib.request, urllib.parse, urllib.error
import settings

class GetError(Exception):
    '''Base class of  SRU API errors'''
    
class GetServerError(GetError):
    '''There was a problem retrieving results from the server.'''
    
class GetParseError(GetError):
    '''There was a problem decoding the response.'''

class Get:
    '''Get SRU for a given CQL query and parse it. Return a list of records.
    Each record is a dictionary of with its title, description, note & tags.
    '''
    def __init__(self, request, query):
        self.query = query
        self.request = request
    
    def namespaces(self):
        return {
            'voc': settings.TAG_SERVER_URL.rstrip('/'),
            'lom': 'http://ltsc.ieee.org/xsd/LOM',
            'zs': 'http://www.loc.gov/zing/srw/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'diagnostic': 'http://www.loc.gov/zing/srw/diagnostic/',
            'srw_dc': 'info:srw/schema/1/dc-schema'
        }

    def string(self, xpath):
        try:
            return xpath[0].text
        except:
            return None

    def get(self):
        ''' Login and get SRU over HTTP.
        '''
        url = '%s?q=sru&operation=searchRetrieve&query=%s' % (
            settings.TAG_SERVER_URL, urllib.parse.quote(self.query)
        )
        try:
            passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, url, settings.TAG_USERNAME, settings.TAG_PASSWORD)
            authhandler = urllib.request.HTTPBasicAuthHandler(passman)
            opener = urllib.request.build_opener(authhandler)
            urllib.request.install_opener(opener)
            urllib.request.urlopen(url).read()
            sru = urllib.request.urlopen(url).read()
        except IOError:
            raise GetServerError("Error accessing the API")
        return sru

    def tags(self, record):
        ''' For a given record return a list of tags as tuples (vocab_id, concept_node_id)
        '''
        ns = self.namespaces()
        lom_ids = [id.text for id in record.xpath("zs:recordData/srw_dc:dc/"
            "lom:classification/lom:taxonPath/"
            "lom:taxon/lom:id", namespaces=ns)]
        lom_strings = [id.text for id in record.xpath("zs:recordData/srw_dc:dc/"
            "lom:classification/lom:taxonPath/"
            "lom:source/lom:string", namespaces=ns)]
        return list(zip(lom_strings, lom_ids))

    def parse(self):
        ''' Return SRU records as dictionaries
        '''
        resp = self.get()
        try:
            sru = etree.XML(resp)
        except Exception as e:
            raise GetParseError("Error parsing SRU XML")
        ns = self.namespaces()
        try:
            msg = sru.xpath("/zs:searchRetrieveResponse/"
                "voc:diagnostics/diagnostic:diagnostic/diagnostic:message", namespaces=ns)
            raise GetServerError(msg.text)
        except:
                records = []
                no_of_records = self.string(sru.xpath("zs:numberOfRecords", namespaces=ns))
                all_records = sru.xpath("zs:records/zs:record", namespaces=ns)
                for record in all_records:
                    print(self.string(record.xpath("zs:recordData/srw_dc:dc/voc:notes", namespaces=ns)))
                    records.append({
                    'title': self.string(record.xpath("zs:recordData/srw_dc:dc/dc:title", namespaces=ns)),
                    'notes': self.string(record.xpath("zs:recordData/srw_dc:dc/voc:notes", namespaces=ns)),
                    'description': self.string(record.xpath("zs:recordData/srw_dc:dc/dc:description", namespaces=ns)),
                    'name': self.string(record.xpath("zs:recordData/srw_dc:dc/voc:name", namespaces=ns)),
                    'node_id': self.string(record.xpath("zs:recordData/srw_dc:dc/"
                        "lom:metaMetadata/lom:identifier/lom:entry", namespaces=ns)),
                    'tags': self.tags(record),
                    'no': no_of_records
                    })
                return records