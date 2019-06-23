"""The index"""

from datetime import datetime
from django.db import models
from django.conf import settings


class Record(models.Model):
    """
    Records with metadata, URL is the primary resource identifier here.
    URLs are organised in dynamic collections of URL patterns and keys.
    To be implemented as methods.
    """
    title = models.CharField(max_length=150)
    desc = models.TextField(blank=True, verbose_name="Description")
    uri = models.URLField(unique=True, verbose_name="URI / Unique Resource ID")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(default=datetime.now, editable=False)
    created_at = models.DateTimeField(default=datetime.now, editable=False)

    def get_absolute_url(self):
        return "/tag/%s" % self.url

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Record, self).save(*args, **kwargs)


class Tag(models.Model):
    """Tags linking concepts to records"""
    record = models.ForeignKey('tag.Record', on_delete=models.CASCADE)
    concept = models.ForeignKey('vocabulary.Concept', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        blank=True, null=True,
        on_delete=models.SET_NULL)
    
    weight = models.IntegerField('Relevance weight of concept'
        'for the record that determines order and importance of tags',
        blank=True, null=True)
    updated_at = models.DateTimeField(default=datetime.now, editable=False)
    created_at = models.DateTimeField(default=datetime.now, editable=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        super(Tag, self).save(*args, **kwargs)
