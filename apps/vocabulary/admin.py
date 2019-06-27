from django.contrib import admin
from django.forms import models, ValidationError
from vocabulary import models as vocabs
from vocabulary.validation_utils import validate_attribute_value
from reversion.admin import VersionAdmin
import re


def clean_relation_value(cleaned_data, obj):
    value = cleaned_data['value']
    attribute = cleaned_data['option']
    success, valid_value = validate_attribute_value(attribute, value, obj)
    if not success:
        raise ValidationError(attribute.error_message)
    return valid_value


class RelationForm(models.ModelForm):
    def clean_validation(self):
        validation = self.cleaned_data['validation']
        try:
            re.compile(validation)
        except:
            raise ValidationError("Invalid regular expression")
        return validation


class RelationInlineForm(models.ModelForm):
    form = RelationForm

    def clean_value(self):
        return clean_relation_value(
            self.cleaned_data,
            self.cleaned_data['concept']
        )


class RelationInline(admin.TabularInline):
    model = vocabs.Relation
    extra = 2
    form = RelationInlineForm
    fk_name = 'subject'
    raw_id_fields = ['predicate', 'object']


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
    inlines = [RelationInline]
    list_display = ('name', 'mother', 'vocabulary', 'forward_path')
    list_filter = ('vocabulary',)
    exclude = ('parent', 'related', 'query')
