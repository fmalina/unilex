from django.contrib import admin
from content.models import Page, Tag

class TagInline(admin.TabularInline):
    model = Tag
    raw_id_fields=('concept',)
    
class PageAdmin(admin.ModelAdmin):
    search_fields = ['title','body']
    list_display = ('title',)
    inlines = [
        TagInline,
    ]
    class Media:
        js = (
            "/js/ckeditor/ckeditor.js",
            "/js/ckeditor-customize.js",
            "/js/ckeditor-attach-admin.js"
        )

admin.site.register(Page, PageAdmin)
