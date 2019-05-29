from django.contrib import admin
from feedback.models import Feedback


def mark_done(modeladmin, request, queryset):
    queryset.update(done=True)


mark_done.short_description = "Mark selected as done"


def unmark_done(modeladmin, request, queryset):
    queryset.update(done=False)


unmark_done.short_description = "Selected are not done"


def mark_awesome(modeladmin, request, queryset):
    queryset.update(awesome=True)


mark_awesome.short_description = "Mark selected as awesome"


def unmark_awesome(modeladmin, request, queryset):
    queryset.update(awesome=False)


unmark_awesome.short_description = "Selected are not awesome"


def mark_ignore(modeladmin, request, queryset):
    queryset.update(ignore=True)


mark_ignore.short_description = "Ignore selected"


def unmark_ignore(modeladmin, request, queryset):
    queryset.update(ignore=False)


unmark_ignore.short_description = "Don't ignore selected"


class FeedbackAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('created_at', 'email', 'message',
                    'url', 'done', 'awesome', 'ignore')
    list_filter = ('created_at', 'done', 'awesome', 'ignore')
    actions = [mark_done, unmark_done, mark_awesome,
               unmark_awesome, mark_ignore, unmark_ignore]


admin.site.register(Feedback, FeedbackAdmin)
