from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from feedback.models import Feedback


def mark_done(modeladmin, request, queryset):
    queryset.update(done=True)


mark_done.short_description = "Mark selected as done"


class FeedbackAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    list_display = ('message', 'email', 'url', 'created_at', 'done')
    list_filter = ('created_at', 'done')
    actions = [mark_done]


admin.site.register(Feedback, FeedbackAdmin)


UserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined')
UserAdmin.ordering = ('-date_joined',)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
