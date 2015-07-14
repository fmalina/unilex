from django.template.loader import render_to_string
import http.client
import settings
from hashlib import md5

def post_tags(record, tags, auth_token):
    ''' Render record and tags in a JSON response
    and POST it as a file attachement.
    Return the server's response page.
    '''
    data = render_to_string('tag/post.js', {
        'record': record,
        'tags': tags
    }).encode("utf-8")
    
    host = '%s' % settings.TAG_SERVER_URL.rstrip('/').lstrip('http://')
    url = '/tags/repository?auth=%s' % auth_token
    h = http.client.HTTPConnection(host)
    h.putrequest('POST', url)
    h.putheader('Content-Disposition', 'filename="data.js"')
    h.putheader('User-Agent', 'Tag')
    h.putheader('content-length', str(len(data)))
    h.endheaders()
    h.send(data)
    return h.getresponse().read()