from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from vocabulary.load_xls import load_xls

class LoadTestCase(TestCase):
    def test_loading(self):
        """Test different types of supported XLS/CSV taxonomy upload"""
        request = RequestFactory().get('/', SERVER_NAME='testserver')
        request.user = User.objects.create_user(
            username='admin', email='x@example.com', password='***')
        request.session='session'
        request._messages = FallbackStorage(request)
        test_files = [
            'taxonomy-with-ids.en-GB.xls',
            'regions-no-ids.xls'
        ]
        
        for fn in test_files:
            with open('vocabulary/test_data/'+fn, 'rb') as f:
                slug = fn.split('.')[0]
                url = load_xls(request, f)
                self.assertEqual(url, '/vocabularies/'+slug+'/')
