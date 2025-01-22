import os

from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from unilex.vocabulary.load_skos import SKOSLoader
from unilex.vocabulary.models import Vocabulary


def create_user():
    user = User.objects.filter(username='admin').first()
    if user:
        return user
    return User.objects.create_user(
        username='admin', email='hi@unilexicon.com', password='admin', is_superuser=True
    )


def setup_site():
    s = Site.objects.get(id=1)
    s.domain = 'unilexicon.com'
    s.name = 'Unilexicon'
    s.save()


def load_vocab(user, path):
    with open(path, 'rb') as f:
        loader = SKOSLoader(user)
        loader.load_skos_vocab(f)
        loader.save_relationships()


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = create_user()
        setup_site()
        for fn in ['World', 'Unilexicon', 'Software', 'Museum']:
            path = os.path.join(settings.BASE_DIR, f'unilex/vocabulary/test_data/vocabs/{fn}.xml')
            Vocabulary.objects.filter(title=fn).delete()
            load_vocab(user, path)
