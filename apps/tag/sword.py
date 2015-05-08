from django.template.loader import render_to_string
import http.client
import settings
from hashlib import md5

def post_sword(record, tags, auth_token):
    ''' Render record and tags in a SWORD XML response
    POST SWORD XML as a file attachement.
    Return the server's response page.
    '''
    sword = render_to_string('tag/SWORD.xml', {
        'record': record,
        'tags': tags
    }).encode("utf-8")
    
    host = '%s' % settings.SRU_SERVER_URL.rstrip('/').lstrip('http://')
    url = '/sword/repository?auth=%s' % auth_token
    h = http.client.HTTPConnection(host)
    h.putrequest('POST', url)
    h.putheader('Content-Disposition', 'filename="sword.xml"')
    h.putheader('X-No-Op', 'false')
    h.putheader('X-Verbose', 'false')
    h.putheader('User-Agent', 'Tagging tool')
    h.putheader('content-length', str(len(sword)))
    h.endheaders()
    h.send(sword)
    return h.getresponse().read()