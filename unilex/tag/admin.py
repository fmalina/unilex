from django.contrib import admin

from unilex.tag.models import Record, Tag


class TagInline(admin.TabularInline):
    model = Tag
    raw_id_fields = ['concept']
    extra = 0


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    search_fields = ['title', 'desc', 'key']
    list_display = ['title', 'key']
    inlines = [TagInline]
