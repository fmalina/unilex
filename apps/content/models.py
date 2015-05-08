from django.db import models
from vocabulary.models import Concept

class Page(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField()
    teaser = models.TextField()
    
    def get_absolute_url(self):
        return "/content/%d" % self.id
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'pages'

class Tag(models.Model):
    concept = models.ForeignKey(Concept)
    page = models.ForeignKey(Page)
    
    def __str__(self):
        return '%s: %s' % (self.page.title, self.concept.forward_path())
    
    class Meta:
        db_table = 'tags'
