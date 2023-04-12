from django.test import TestCase
from django.test.client import RequestFactory

from django.contrib.messages.storage.fallback import FallbackStorage
from unilex.vocabulary.management.commands.dev_setup import create_user
from unilex.vocabulary.load_xls import load_xls
from unilex.vocabulary.load_md import load_md


class LoadTestCase(TestCase):
    def test_loading(self):
        """Test different types of supported XLS/CSV taxonomy upload"""
        request = RequestFactory().get('/', SERVER_NAME='testserver')
        request.user = create_user()
        request.session = 'session'
        request._messages = FallbackStorage(request)
        test_files = [
            (5427, 'taxonomy-with-ids.xls'),
            (269, 'world-with-ids.csv'),
            (28, 'world-no-ids1.xls'),
            (28, 'world-no-ids.csv'),
            (17, 'artificial-intelligence.md'),
            (17, 'personal-safety.md'),
            (9, 'watches.md')
        ]
        load_ext = {
            'csv': load_xls,
            'xls': load_xls,
            'md': load_md,
        }
        for no, fn in test_files:
            with open('unilex/vocabulary/test_data/'+fn, 'rb') as f:
                slug, ext = fn.split('.')
                v = load_ext[ext](request.user, f.read(), slug)
                self.assertEqual(v.get_absolute_url(),
                                 f'/tree/{slug}/')
                self.assertEqual(no, v.concept_set.all().count())
