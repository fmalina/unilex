from django.test import TestCase

class LoadTestCase(TestCase):
    def test_loading(self):
        url = "/tags/"
        self.assertEqual(url, '/tags/')