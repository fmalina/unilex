from django.contrib import admin
from django.forms import models, ValidationError
from unilex.vocabulary import models as vocabs
from unilex.vocabulary.validation_utils import validate_attribute_value
from reversion.admin import VersionAdmin


def clean_relation_value(cleaned_data, obj):
    value = cleaned_data['value']
    attribute = cleaned_data['option']
    success, valid_value = validate_attribute_value(attribute, value, obj)
    if not success:
        raise ValidationError(attribute.error_message)
    return valid_value


class RelationInlineForm(models.ModelForm):
    def clean_value(self):
        return clean_relation_value(self.cleaned_data, self.cleaned_data['concept'])


class RelationInline(admin.TabularInline):
    model = vocabs.Relation
    extra = 2
    form = RelationInlineForm
    fk_name = 'subject'
    raw_id_fields = ['predicate', 'object']


@admin.register(vocabs.Language)
class LanguageAdmin(admin.ModelAdmin):
    admin.site.disable_action(
        'delete_selected',
    )


class AuthorityMembershipInline(admin.TabularInline):
    model = vocabs.Authority.users.through
    raw_id_fields = ['user']


@admin.register(vocabs.Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    inlines = [AuthorityMembershipInline]
    exclude = ['users']


def bulk_delete(modeladmin, request, queryset):
    queryset.delete()


bulk_delete.short_description = 'Delete selected'


@admin.register(vocabs.Vocabulary)
class VocabularyAdmin(VersionAdmin):
    actions = [bulk_delete]
    search_fields = ['node_id', 'title', 'description']
    prepopulated_fields = {'node_id': ('title',)}
    list_filter = ('private',)
    list_display = ('title', 'node_id', 'user', 'language', 'private', 'updated_at', 'created_at')


@admin.register(vocabs.Concept)
class ConceptAdmin(VersionAdmin):
    search_fields = ['id', 'name']
    inlines = [RelationInline]
    list_display = ('name', 'mother', 'vocabulary', 'forward_path')
    list_filter = ('vocabulary',)
    exclude = ('parent', 'related', 'query')
