from django.contrib import admin

from .models import (
    Assignment,
    AssignmentProgress,
    AssignmentNotification,
    ClassGroup,
    GroupMembership,
    EmailVerification,
    LoginAttempt,
    PushSubscription,
)


@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = (
        "course_name",
        "section",
        "academic_year",
        "semester",
        "invite_code",
    )
    search_fields = ("course_name", "section", "invite_code")


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
