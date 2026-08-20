from django.contrib import admin

from .models import (
    Assignment,
    AssignmentProgress,
    AssignmentNotification,
    ClassGroup,
    GroupMembership,
    EmailVerification,
    LoginAttempt,
    PeerReminder,
    PushSubscription,
)


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "invite_code", "created_by", "created_at")
    search_fields = ("name", "description", "invite_code")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "due_at", "created_by")
    list_filter = ("group",)


admin.site.register(GroupMembership)
admin.site.register(AssignmentProgress)
admin.site.register(PushSubscription)
admin.site.register(AssignmentNotification)
admin.site.register(EmailVerification)
admin.site.register(LoginAttempt)
admin.site.register(PeerReminder)
