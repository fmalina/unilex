from django.contrib import admin
from django.forms import models, ValidationError
from vocabulary import models as vocabs
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
    model = vocabs.ConceptAttribute
    extra = 2
    form = ConceptAttributeInlineForm


class LanguageAdmin(admin.ModelAdmin):
    admin.site.disable_action('delete_selected',)


class AuthorityAdmin(admin.ModelAdmin):
    pass


class VocabularyAdmin(admin.ModelAdmin):
    prepopulated_fields = {"node_id": ("title",)}
    list_display = ('title', 'node_id', 'user', 'language',
                    'private', 'updated_at', 'created_at')


class ConceptAdmin(admin.ModelAdmin):
    search_fields = ['id','name']
    inlines = [ConceptAttribute_Inline]
    list_display = ('name', 'mother', 'vocabulary', 'forward_path')
    list_filter = ('vocabulary',)
    exclude = ('parent', 'related', 'query')


admin.site.register(vocabs.Language, LanguageAdmin)
admin.site.register(vocabs.Concept, ConceptAdmin)
admin.site.register(vocabs.Vocabulary, VocabularyAdmin)
admin.site.register(vocabs.AttributeOption, AttributeOptionAdmin)
admin.site.register(vocabs.Authority, AuthorityAdmin)
