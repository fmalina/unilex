from django.test import TestCase


class TaggingTestCase(TestCase):

    def test_tagging(self):
        foo = 'bar'
        self.assertEqual(foo, 'bar')
