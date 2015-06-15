from django.contrib import admin
from django.forms import models, ValidationError
from vocabulary.models import Vocabulary, Concept, Language, ConceptAttribute, AttributeOption
from vocabulary.validation_utils import validate_attribute_value
import re

def clean_attribute_value(cleaned_data, obj):
    value = cleaned_data['value']
    attribute = cleaned_data['option']
    success, valid_value = validate_attribute_value(attribute, value, obj)
    if not success:
        raise ValidationError(attribute.error_message)
    return valid_value

class AttributeOptionForm(models.ModelForm):
    def clean_validation(self):
        validation = self.cleaned_data['validation']
        try:
            re.compile(validation)
        except:
            raise ValidationError("Invalid regular expression")
        return validation

class AttributeOptionAdmin(admin.ModelAdmin):
    form = AttributeOptionForm
    prepopulated_fields = {"name": ("description",)}

class ConceptAttributeInlineForm(models.ModelForm):
    def clean_value(self):
        return clean_attribute_value(self.cleaned_data, self.cleaned_data['concept'])

class ConceptAttribute_Inline(admin.TabularInline):
    model = ConceptAttribute
    extra = 2
    form = ConceptAttributeInlineForm

class LanguageAdmin(admin.ModelAdmin):
    #admin.site.disable_action('delete_selected',)
    pass

class VocabularyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"node_id": ("title",)}
    list_display = ('title','node_id','user','language','private','updated_at','created_at')

class ConceptAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    inlines = [ConceptAttribute_Inline]
    list_display = ('name','mother','vocabulary','forward_path')
    list_filter = ('vocabulary',)
    exclude = ('parent','related','node_id')

admin.site.register(Language, LanguageAdmin)
admin.site.register(Concept, ConceptAdmin)
admin.site.register(Vocabulary, VocabularyAdmin)
admin.site.register(AttributeOption, AttributeOptionAdmin)