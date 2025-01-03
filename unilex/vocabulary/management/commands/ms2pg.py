from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.fields.related import ManyToManyField
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from allauth.account.models import EmailAddress
from pay.models import Subscription, Payment
from unilex.vocabulary.models import Vocabulary, Concept, Authority, Language, Relation
from unilex.feedback.models import Feedback
from unilex.tag.models import Tag, Record


class Command(BaseCommand):
    help = 'Migrate data from MySQL to Postgres'
    models_to_migrate = [
        SocialApp,
        User,
        SocialAccount,
        SocialToken,
        EmailAddress,
        Subscription, Payment,
        Language, Authority, Vocabulary, Concept, Relation,
        Feedback,
        Record, Tag
    ]

    def handle(self, *args, **kwargs):
        for model in self.models_to_migrate:
            self.migrate_model(model)
        for model in self.models_to_migrate:
            self.migrate_m2m_fields(model)
        self.fix_site()

    def migrate_model(self, model):
        self.stdout.write(f"Migrating {model.__name__}...")
        legacy_qs = model.objects.using('legacy').all()
        new_objects = []
        for obj in legacy_qs:
            new_obj = model()  # Create a new instance for the default database
            for field in model._meta.fields:
                if field.is_relation:
                    setattr(new_obj, field.name + "_id", getattr(obj, field.name + "_id"))
                else:
                    setattr(new_obj, field.name, getattr(obj, field.name))
            new_objects.append(new_obj)

        # Bulk create objects in the default database
        with transaction.atomic(using='default'):
            model.objects.using('default').bulk_create(new_objects, batch_size=1000)

    def migrate_m2m_fields(self, model):
        m2m_fields = [f for f in model._meta.get_fields()
                      if isinstance(f, ManyToManyField)]

        legacy_qs = model.objects.using('legacy').all()
        if m2m_fields:
            self.stdout.write(f"Migrating {model.__name__} with {', '.join([f.name for f in m2m_fields])}")
        # Handle ManyToMany fields
        for m2mfield in m2m_fields:
            nm = m2mfield.name
            self.stdout.write(f"    copying data for {nm}...")
            for obj in legacy_qs:
                new_obj = model.objects.using('default').get(pk=obj.pk)
                m2m_data_legacy = getattr(obj, nm).using('legacy').all()
                m2m_data_default = [
                    type(m2m_obj).objects.using('default').get(pk=m2m_obj.pk)
                    for m2m_obj in m2m_data_legacy
                ]
                # Set M2M relationships
                getattr(new_obj, nm).set(m2m_data_default)
        self.stdout.write(f"    done")

    def fix_site(self):
        s = Site.objects.get(pk=1)
        s.name = 'Unilexicon'
        s.domain = 'unilexicon.co'
        s.save()
