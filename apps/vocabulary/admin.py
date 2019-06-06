from django.contrib import admin
from django.forms import models, ValidationError
from vocabulary import models as vocabs
from vocabulary.validation_utils import validate_attribute_value
from reversion.admin import VersionAdmin
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


@admin.register(vocabs.AttributeOption)
class AttributeOptionAdmin(admin.ModelAdmin):
    form = AttributeOptionForm
    prepopulated_fields = {"name": ("description",)}


class ConceptAttributeInlineForm(models.ModelForm):
    def clean_value(self):
        return clean_attribute_value(
            self.cleaned_data,
            self.cleaned_data['concept']
        )


class ConceptAttribute_Inline(admin.TabularInline):
    model = vocabs.ConceptAttribute
    extra = 2
    form = ConceptAttributeInlineForm


@admin.register(vocabs.Language)
class LanguageAdmin(admin.ModelAdmin):
    admin.site.disable_action('delete_selected',)


class AuthorityMembershipInline(admin.TabularInline):
    model = vocabs.Authority.users.through
    raw_id_fields = ['user']

@admin.register(vocabs.Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    inlines = [AuthorityMembershipInline]
    exclude = ['users']


@admin.register(vocabs.Vocabulary)
class VocabularyAdmin(VersionAdmin):
    prepopulated_fields = {"node_id": ("title",)}
    list_display = (
        'title', 'node_id', 'user', 'language',
        'private', 'updated_at', 'created_at'
    )


@admin.register(vocabs.Concept)
class ConceptAdmin(VersionAdmin):
    search_fields = ['id','name']
    inlines = [ConceptAttribute_Inline]
    list_display = ('name', 'mother', 'vocabulary', 'forward_path')
    list_filter = ('vocabulary',)
    exclude = ('parent', 'related', 'query')
