from django.contrib import admin
from django.utils.html import format_html
from .models import AllowedEmail


@admin.register(AllowedEmail)
class AllowedEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'added_by', 'role_badge')
    list_filter = ('role',)
    search_fields = ('email', 'added_by')
    ordering = ('email',)

    # Which fields appear in the add/change form
    fields = ('email', 'role', 'added_by')

    def role_badge(self, obj):
        colors = {
            'admin':  '#6366f1',
            'user':   '#10b981',
            'viewer': '#f59e0b',
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8em;">{}</span>',
            color, obj.role
        )
    role_badge.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        # Always store email in lowercase to avoid case-mismatch on login
        obj.email = obj.email.lower().strip()
        if not obj.added_by:
            obj.added_by = request.user.email
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # Don't allow changing the email once it's been set
        if obj:
            return ('email',)
        return ()
