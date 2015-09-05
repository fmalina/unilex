from django.contrib import admin
from tag.models import Record, Tag

class TagInline(admin.TabularInline):
    model = Tag
    raw_id_fields = ['concept']
    extra = 0
    
class RecordAdmin(admin.ModelAdmin):
    search_fields = ['title','desc','url']
    list_display = ('title','url',)
    inlines = [TagInline]

admin.site.register(Record, RecordAdmin)
