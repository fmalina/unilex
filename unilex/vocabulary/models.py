import uuid
from datetime import datetime

from django.conf import settings
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags

import reversion


class Language(models.Model):
    """Language of a vocabulary or Concept label"""

    iso = models.CharField(primary_key=True, max_length=5, verbose_name='ISO code')
    name = models.CharField(max_length=60)

    def __str__(self):
        return self.iso

    class Meta:
        db_table = 'languages'


class Authority(models.Model):
    """Authority is an organisation, author or maintainer whose
    decisions on development of a vocabulary are definitive"""
    code = models.CharField(
        max_length=5, primary_key=True,
        help_text='Uppercase shorthand, no spaces, only set once')
    name = models.CharField(max_length=150)
    website = models.URLField(blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        help_text='Authority can have many users. Vocabulary can have one authority.')

    def __str__(self):
        return self.code

    class Meta:
        verbose_name_plural = 'Authorities'


class VocabularyManager(models.Manager):
    def with_counts(self):
        return self.annotate(concept_count=models.Count('concept'))


def uniq_slug(slug):
    uid = str(uuid.uuid4())[:5]
    return f"{slug}--{uid}"


@reversion.register()
class Vocabulary(models.Model):
    """Vocabulary is a hierarchy of concepts"""

    node_id = models.SlugField(unique=True, max_length=60, verbose_name='Permalink: /vocabularies/')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    title = models.CharField(max_length=75)
    description = models.TextField(max_length=200, blank=True, null=True)
    language = models.ForeignKey(Language, blank=True, null=True, on_delete=models.PROTECT)
    authority = models.ForeignKey(Authority, blank=True, null=True, on_delete=models.PROTECT)
    queries = models.BooleanField(verbose_name="Enable queries?", default=False)
    private = models.BooleanField(
        verbose_name="Private vocabulary", default=True,
        help_text="Private vocabulary can be edited only by the users belonging to its authority.")
    source = models.URLField(blank=True)
    updated_at = models.DateTimeField(default=datetime.now, editable=False)
    created_at = models.DateTimeField(default=datetime.now, editable=False)

    objects = VocabularyManager()

    @property
    def name(self):
        return self.title

    def get_children(self):
        return self.concept_set.filter(parent__isnull=True).order_by('order')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/vocabularies/{self.node_id}/'

    def json_url(self):
        return f'/vocabularies/{self.node_id}/json'

    def make_node_id(self, slugbase):
        slug = slugify(slugbase)
        if Vocabulary.objects.filter(node_id__iexact=slug).exists():
            return uniq_slug(slug)
        return slug

    def is_allowed_for(self, user):
        """Say whether this user has permission to access this vocab."""
        if self.authority and user in self.authority.users.all():
            return True
        if user.pk == self.user.pk:
            return True
        if user.is_superuser or user.is_staff:
            return True
        return False

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        if not self.pk and not self.node_id or self.node_id.startswith('new-vocabulary'):
            # must be a new vocabulary or excel import without node_id
            self.node_id = self.make_node_id(self.title)
        if not self.pk:
            # must be an import and nodeID has been provided
            self.node_id = self.make_node_id(self.node_id)
        self.node_id = slugify(self.node_id)
        super(Vocabulary, self).save(*args, **kwargs)

    class Meta:
        db_table = 'vocabularies'
        verbose_name_plural = 'Vocabularies'


@reversion.register()
class Concept(models.Model):
    """A Concept is a term within a vocabulary"""

    node_id = models.SlugField('Permalink ID', db_index=True, max_length=127, blank=True)
    vocabulary = models.ForeignKey('vocabulary.Vocabulary', on_delete=models.CASCADE)
    name = models.CharField(db_index=True, max_length=255)  # prefLabel
    description = models.TextField(blank=True)
    order = models.IntegerField(blank=True, null=True)
    parent = models.ManyToManyField('self', blank=True, symmetrical=False,
                                    related_name='children')
    related = models.ManyToManyField('self', blank=True, symmetrical=False,
                                     related_name='relations',
                                     through='vocabulary.Relation',
                                     through_fields=('subject', 'predicate'))
    query = models.TextField(blank=True)
    count = models.IntegerField(blank=True, null=True)
    active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(default=datetime.now, editable=False)
    created_at = models.DateTimeField(default=datetime.now, editable=False)

    def mother(self):
        return self.parent.first()

    def _recurse_for_parents(self, o):
        ls = []
        if o:
            parent = o.mother()
            ls.append(parent)
            if parent != self:
                ls += self._recurse_for_parents(parent)
        if o == self and ls:
            ls.reverse()
        return ls

    def get_children(self):
        return self.children.prefetch_related('vocabulary').order_by('order')

    def get_descendants(self):
        ls = list(self.get_children())
        for c in ls:
            ls += list(c.get_descendants())
        return ls

    def breadcrumb(self):
        ls = self._recurse_for_parents(self)
        ls.pop(0)
        return [self.vocabulary] + ls + [self]

    def get_path(self):
        return [x.name for x in self.breadcrumb()]

    def level(self):
        return len(self.get_path())

    def depth_indent(self):
        return (self.level() - 2) * ','

    def forward_path(self):
        return strip_tags(' » '.join(self.get_path()))

    def backwards_path(self):
        p = self.get_path()
        p.reverse()
        return ' « '.join(p)

    def get_absolute_url(self):
        return f'{self.vocabulary.get_absolute_url()}#c-{self.node_id}'

    def get_edit_url(self):
        return f'/vocabularies/{self.vocabulary.node_id}/{self.node_id}/'

    def __str__(self):
        return self.name

    def make_node_id(self):
        slug = slugify(self.name)
        if Concept.objects.filter(node_id__iexact=slug,
                                  vocabulary=self.vocabulary).exists():
            return uniq_slug(slug)
        return slug

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        if not self.node_id:
            self.node_id = self.make_node_id()
        super(Concept, self).save(*args, **kwargs)

    class Meta:
        db_table = 'concepts'
        ordering = ['order', 'name']
        unique_together = [('node_id', 'vocabulary')]


class Relation(models.Model):
    """Simple related concepts, custom relation triples, synonyms, attribute values etc."""
    VALUE_TYPES = [
        ('char', 'vocabulary.validation_utils.validation_simple', 'One or more characters'),
        ('bool', 'vocabulary.validation_utils.validation_yesno', 'Yes or No'),
        ('json', 'vocabulary.validation_utils.validation_json', 'Valid JSON'),
        ('int', 'vocabulary.validation_utils.validation_integer', 'Integer number'),
        ('dec', 'vocabulary.validation_utils.validation_decimal', 'Decimal number'),
    ]
    VALUE_TYPE_CHOICES = [(x, z) for x, y, z in VALUE_TYPES]
    VALIDATIONS = [(y, z) for x, y, z in VALUE_TYPES]

    subject = models.ForeignKey(Concept, related_name='subject', on_delete=models.CASCADE)
    predicate = models.ForeignKey(Concept, related_name='predicate', on_delete=models.CASCADE)
    object = models.ForeignKey(Concept, related_name='object', on_delete=models.CASCADE, null=True, blank=True)
    object_value_type = models.CharField("Object type", choices=VALUE_TYPE_CHOICES, max_length=4, null=True, blank=True)
    object_value = models.TextField("Object value", null=True, blank=True)

    @property
    def name(self):
        return self.object.name

    @property
    def description(self):
        return self.object.description

    class Meta:
        db_table = 'concept_relations'
        verbose_name = "Concept Relation"
        verbose_name_plural = "Concept Relations"

    def __str__(self):
        return self.object.name
