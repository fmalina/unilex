from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from unilex.feedback.models import Feedback


def mark_done(modeladmin, request, queryset):
    queryset.update(done=True)


def delete_spam(modeladmin, request, queryset):
    queryset.delete()


mark_done.short_description = 'Mark selected as done'
delete_spam.short_description = 'Delete selected'


class FeedbackAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('id', 'done', 'message', 'email', 'url', 'created_at')
    list_filter = ('created_at', 'done')
    actions = [mark_done, delete_spam]


admin.site.register(Feedback, FeedbackAdmin)


UserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined')
UserAdmin.ordering = ('-date_joined',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
