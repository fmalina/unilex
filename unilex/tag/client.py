import http.client
import urllib.error
import urllib.parse
import urllib.request

from django.template.loader import render_to_string


class Client:
    """Get tags for a given query and parse. Return a list of records.
    Each record is a dictionary of with its title, description, note & tags.
    """

    TAG_SERVER_HOST = '127.0.0.1:8000'
    TAG_SERVER_URL = 'http://' + TAG_SERVER_HOST + '/'

    def __init__(self, request, query):
        self.query = query
        self.request = request

    def get_tags(self, api_key=""):
        """Get tags over HTTP and return records as dictionaries
        """
        url = self.TAG_SERVER_URL + 'tag/json/' + urllib.parse.quote(self.query) + api_key
        data = urllib.request.urlopen(url).read().decode()
        return data

    def post_tags(self, record, tags, api_key):
        """Render record and tags in a JSON response and POST as a file attachement.
        Return the server's response.
        """
        data = render_to_string('tag/record.js', {'record': record, 'tags': tags})
        host = f'{self.TAG_SERVER_HOST}'
        url = '/tag/repository?api_key=' + api_key
        h = http.client.HTTPConnection(host)
        h.putrequest('POST', url)
        h.putheader('Content-Disposition', 'filename="data.js"')
        h.putheader('User-Agent', 'Tag')
        h.putheader('content-length', str(len(data)))
        h.endheaders()
        h.send(data)
        return h.getresponse().read()
