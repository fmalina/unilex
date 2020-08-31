from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from unilex.vocabulary.load_skos import SKOSLoader
from unilex.vocabulary.models import Vocabulary


def create_user():
    user = User.objects.filter(username='admin').first()
    if user:
        return user
    return User.objects.create_user(
        username='admin',
        email='hi@unilexicon.com',
        password='admin',
        is_superuser=True
    )


def setup_site():
    s = Site.objects.get(id=1)
    s.domain = "unilexicon.com"
    s.name = "Unilexicon"
    s.save()


def load_vocab(user, fn):
    path = f"{settings.PROJECT_ROOT}apps/vocabulary/test_data/vocabs/{fn}.xml"
    with open(path, 'rb') as f:
        loader = SKOSLoader(user)
        loader.load_skos_vocab(f)
        loader.save_relationships()


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = create_user()
        setup_site()
        for fn in ['World', 'Unilexicon', 'Software', 'Museum']:
            Vocabulary.objects.filter(title=fn).delete()
            load_vocab(user, fn)
