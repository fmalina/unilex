from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from vocabulary.load_xls import load_xls
from vocabulary.models import Vocabulary


class LoadTestCase(TestCase):
    def test_loading(self):
        """Test different types of supported XLS/CSV taxonomy upload
        """
        request = RequestFactory().get('/', SERVER_NAME='testserver')
        request.user = User.objects.create_user(
            username='admin', email='x@example.com', password='***')
        request.session='session'
        request._messages = FallbackStorage(request)
        test_files = [
            (5427, 'taxonomy-with-ids.en-GB.xls'),
            (269, 'world-with-ids.UN-001.csv'),
            (28, 'world-no-ids1.xls'),
            (28, 'world-no-ids.csv'),
            (28, 'world-with-ids-parents.csv')
        ]
        
        for no, fn in test_files:
            with open('vocabulary/test_data/'+fn, 'rb') as f:
                slug = fn.split('.')[0]
                url = load_xls(request, f.read(), slug)
                self.assertEqual(url, '/vocabularies/'+slug+'/')
                v = Vocabulary.objects.all().last()
                self.assertEqual(no, v.concept_set.all().count())
