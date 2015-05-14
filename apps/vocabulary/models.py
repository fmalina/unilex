from django.db import models
from django.conf import settings
from django.utils.html import strip_tags, strip_entities
from django.template.defaultfilters import slugify
from vocabulary.baseconv import base36
from datetime import datetime
import random
import re
import time

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
    code = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=150)
    # users = models.ManyToManyField(settings.AUTH_USER_MODEL,
    #     help_text="Authority can have many users. Vocabulary can have one authority.")
    
    def __str__(self):
        return self.code

class VocabularyManager(models.Manager):
    def with_counts(self):
        return self.annotate(concept_count=models.Count('concept'))

class Vocabulary(models.Model):
    """Vocabulary is a hierarchy of concepts"""
    node_id     = models.SlugField(db_index=True, max_length=60, verbose_name='Permalink: /vocabularies/')
    title       = models.CharField(max_length=75)
    description = models.TextField(max_length=200, blank=True, null=True)
    language    = models.ForeignKey(Language, blank=True, null=True)
    authority   = models.ForeignKey(Authority, blank=True, null=True)
    queries     = models.BooleanField(verbose_name="Enable queries?", default=False)
    private     = models.BooleanField(verbose_name="Private vocabulary", default=False,
        help_text="Private vocabulary can be edited only by the users belonging to its authority.")
    updated_at  = models.DateTimeField(default=datetime.now, editable=False)
    created_at  = models.DateTimeField(default=datetime.now, editable=False)

    objects = VocabularyManager()
    
    def get_children(self):
        return Concept.objects.filter(vocabulary=self, parent__isnull=True).order_by('order')
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return '/vocabularies/%s/' % self.node_id

    def increment_slug(self, slug):
        current_number_suffix_match = re.search("\d+$", slug) # get the current number suffix if there is one
        current_number_suffix = current_number_suffix_match and current_number_suffix_match.group() or 0
        next = str(int(current_number_suffix) +1) # increment it, and turn back to string so re.sub doesn't die
        return re.sub("(\d+)?$", next, slug) # replace current number suffix with incremented suffix, try again...

    def make_node_id(self, slugbase):
        slug = slugify(slugbase)
        while(Vocabulary.objects.filter(node_id__iexact=slug).count()): # if it's not unique
            slug = self.increment_slug(slug)
        return slug

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        if not self.pk and not self.node_id:
            # must be a new vocabulary or excel import without node_id
            self.node_id = self.make_node_id(self.title)
        if not self.pk:
            # must be an import and nodeID has been provided
            self.node_id = self.make_node_id(self.node_id)
            
        super(Vocabulary, self).save(*args, **kwargs)

    class Meta:
        db_table = 'vocabularies'
        verbose_name_plural = "Vocabularies"

class Concept(models.Model):
    """A Concept is a term within a vocabulary."""
    node_id     = models.SlugField(db_index=True, max_length=60, blank=True)
    vocabulary  = models.ForeignKey(Vocabulary)
    name        = models.CharField(db_index=True, max_length=255) # prefLabel
    description = models.TextField(blank=True)
    order       = models.IntegerField(blank=True, null=True)
    parent      = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='children')
    related     = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='related_concepts')
    query       = models.TextField(blank=True)
    count       = models.IntegerField(blank=True, null=True)
    active      = models.BooleanField(default=True)
    updated_at  = models.DateTimeField(default=datetime.now, editable=False)
    created_at  = models.DateTimeField(default=datetime.now, editable=False)
    
    def mother(self):
        try:
            return self.parent.all()[0]
        except:
            return None
    
    def _recurse_for_parents(self, concept_obj):
        parent_list = []
        try:
            parent = concept_obj.mother()
            parent_list.append(parent)
            if parent != self:
                more = self._recurse_for_parents(parent)
                parent_list.extend(more)
        except:
            pass
        if concept_obj == self and parent_list:
            parent_list.reverse()
        return parent_list
    
    def get_children(self):
        return Concept.objects.filter(parent=self).order_by('order')
    
    def get_descendants(self):
        all = []
        children = list(self.get_children())
        all.extend(children)
        for child in children:
            all.extend(list(child.get_descendants()))
        return all
    
    def get_descendants_count(self):
        return len(self.get_descendants())
    
    def get_path(self):
        concept_list = self._recurse_for_parents(self)
        name_list = []
        for c in concept_list:
            name_list.append(str(c))
        name_list.pop(0)
        gotpath = [self.vocabulary.title,]
        gotpath.extend(name_list)
        gotpath.append(self.name)
        return gotpath
    
    def breadcrumb(self):
        concept_list = self._recurse_for_parents(self)
        concept_list.pop(0)
        gotpath = [self.vocabulary]
        gotpath.extend(concept_list)
        gotpath.append(self)
        return gotpath
    
    def depth_indent(self):
        depth = ''
        i = 0
        for p in self.get_path():
            if i > 1:
                depth = '%s,' % depth
            i = i+1
        return depth

    def forward_path(self):
        return strip_entities(strip_tags(' » '.join(self.get_path())))

    def backwards_path(self):
        p = self.get_path()
        p.reverse()
        return ' « '.join(p)

    def get_absolute_url(self):
        return '%s#c-%s' % (self.vocabulary.get_absolute_url(), self.node_id)

    def get_edit_url(self):
        return '/vocabularies/%s/%s/' % (self.vocabulary.node_id, self.node_id)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        if not self.node_id:
            # make a short hash based on current time http://www.google.com/logos/unix1234567890.gif
            # reverse it for easier autocompletion (striding backwards)
            self.node_id = base36.from_decimal(int((time.time() - 1234567890) * 1000000))[::-1]
        super(Concept, self).save(*args, **kwargs)
        
    class Meta:
        db_table = 'concepts'
        ordering = 'name',
        unique_together = ('node_id', 'vocabulary')

class Synonym(models.Model):
    concept = models.ForeignKey(Concept)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'concepts_synonyms'
        unique_together = ('concept', 'name')




# custom fields - not implemeted

VALIDATIONS = [
    ('vocabulary.validation_utils.validation_simple',  'One or more characters'),
    ('vocabulary.validation_utils.validation_integer', 'Integer number'),
    ('vocabulary.validation_utils.validation_yesno',   'Yes or No'),
    ('vocabulary.validation_utils.validation_decimal', 'Decimal number'),
]

class AttributeOption(models.Model):
    """
    Type of a note
    
    Allows arbitrary name/value pairs to be attached to a concept.
    By defining the list, the user will be presented with a predefined
    list of attributes instead of a free form field.
    The validation field should contain a regular expression that can be
    used to validate the structure of the input.
    Possible usage for a book: ISBN, Pages, Author, etc
    """
    description   = models.CharField("Description", max_length=100)
    name          = models.SlugField("Attribute name", max_length=100)
    validation    = models.CharField("Field Validations", choices=VALIDATIONS, max_length=100)
    sort_order    = models.IntegerField("Sort Order", default=1)
    error_message = models.CharField("Error Message", default="Invalid Entry", max_length=100)

    class Meta:
        db_table = 'concepts_attribute_options'
        ordering = ('sort_order',)

    def __str__(self):
        return self.description


class ConceptAttribute(models.Model):
    """
    Allows arbitrary name/value pairs (as strings) to be attached to a concept.
    This is a simple way to add extra text or numeric info to a concept.
    If you want more structure than this, create your own subtype to add
    whatever you want to your Concepts.
    """
    concept      = models.ForeignKey(Concept)
    #languagecode = models.CharField(_('language'), max_length=10, choices=settings.LANGUAGES, null=True, blank=True)
    option       = models.ForeignKey(AttributeOption)
    value        = models.CharField("Value", max_length=255)

    @property
    def name(self):
        return self.option.name

    @property
    def description(self):
        return self.option.description

    class Meta:
        db_table = 'concepts_attributes'
        verbose_name = "Note: Concept Attribute"
        verbose_name_plural = "Notes: Concept Attributes"

    def __str__(self):
        return self.option.name