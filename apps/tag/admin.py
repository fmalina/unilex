from django.contrib import admin
from tag.models import Page, Tag

class TagInline(admin.TabularInline):
    model = Tag
    raw_id_fields=('concept',)
    
class PageAdmin(admin.ModelAdmin):
    search_fields = ['title','body']
    list_display = ('title',)
    inlines = [
        TagInline,
    ]

admin.site.register(Page, PageAdmin)
