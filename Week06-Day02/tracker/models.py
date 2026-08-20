import secrets

from django.conf import settings
from django.db import models


def create_invite_code():
    return secrets.token_hex(4).upper()


def create_verification_token():
    return secrets.token_urlsafe(32)


class ClassGroup(models.Model):
    name = models.CharField("그룹 이름", max_length=100)
    description = models.TextField("그룹 설명", blank=True)
    show_member_progress = models.BooleanField(
        "구성원 진행 상태 공개",
        default=False,
        help_text="그룹 구성원이 서로의 과제 진행 상태를 확인하고 미완료 구성원을 찌를 수 있습니다.",
    )
    invite_code = models.CharField(
        "초대 코드", max_length=8, unique=True, default=create_invite_code, editable=False
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_class_groups",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "-created_at"]

    def __str__(self):
        return self.name


class GroupMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "관리자"
        MEMBER = "member", "구성원"

    group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="class_memberships",
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["group", "user"], name="unique_group_member")
        ]


class Assignment(models.Model):
    group = models.ForeignKey(
        ClassGroup, on_delete=models.CASCADE, related_name="assignments"
    )
    title = models.CharField("과제명", max_length=150)
    description = models.TextField("설명", blank=True)
    due_at = models.DateTimeField("제출 마감")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "title", "due_at"],
                name="unique_assignment_in_group",
            )
        ]

    def __str__(self):
        return f"{self.group.name} - {self.title}"


class AssignmentProgress(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "시작 전"
        DOING = "doing", "진행 중"
        DONE = "done", "완료"

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="progress_records"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_progress",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.TODO)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "user"], name="unique_assignment_progress"
            )
        ]


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_webpush_info(self):
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }


class AssignmentNotification(models.Model):
    class Kind(models.TextChoices):
        BEFORE_DUE = "before_due", "마감 전"
        OVERDUE = "overdue", "마감 초과"

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="notification_records"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_notifications",
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    scheduled_for = models.DateTimeField("알림 기준 시각")
    sent_at = models.DateTimeField("발송 시각", null=True, blank=True)
    attempt_count = models.PositiveSmallIntegerField(default=0)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_for"]
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "user", "scheduled_for"],
                name="unique_assignment_notification_schedule",
            )
        ]


class PeerReminder(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="peer_reminders"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_peer_reminders",
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_peer_reminders",
    )
    delivered_count = models.PositiveSmallIntegerField(default=0)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]


class EmailVerification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification",
    )
    token = models.CharField(max_length=64, unique=True, default=create_verification_token)
    created_at = models.DateTimeField(auto_now_add=True)


class LoginAttempt(models.Model):
    identifier = models.CharField(max_length=255, unique=True)
    failure_count = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
