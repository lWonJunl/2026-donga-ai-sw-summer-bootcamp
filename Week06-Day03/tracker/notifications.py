import json
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.utils import timezone
from pywebpush import WebPushException, webpush

from .models import (
    Assignment,
    AssignmentNotification,
    AssignmentProgress,
    GroupMembership,
)


PRE_DUE_HOURS = (72, 24, 12, 6, 3, 2, 1, 0.5)
OVERDUE_INTERVAL = timedelta(hours=6)


@dataclass(frozen=True)
class NotificationSlot:
    kind: str
    scheduled_for: object
    label: str


def current_notification_slot(due_at, now=None):
    """Return only the latest crossed slot so a late job never sends a burst."""
    now = now or timezone.now()

    if now >= due_at:
        period = int((now - due_at) // OVERDUE_INTERVAL)
        scheduled_for = due_at + (OVERDUE_INTERVAL * period)
        label = "마감 초과" if period == 0 else f"마감 {period * 6}시간 초과"
        return NotificationSlot(
            AssignmentNotification.Kind.OVERDUE, scheduled_for, label
        )

    crossed = []
    for hours in PRE_DUE_HOURS:
        scheduled_for = due_at - timedelta(hours=hours)
        if now >= scheduled_for:
            label = "30분" if hours == 0.5 else f"{int(hours)}시간"
            crossed.append(
                NotificationSlot(
                    AssignmentNotification.Kind.BEFORE_DUE,
                    scheduled_for,
                    label,
                )
            )
    return max(crossed, key=lambda slot: slot.scheduled_for) if crossed else None


def _notification_payload(assignment, slot):
    if slot.kind == AssignmentNotification.Kind.OVERDUE:
        body = (
            f"{assignment.group.name} · {assignment.title} 과제가 "
            f"{slot.label} 상태입니다. 제출 여부를 확인하세요."
        )
    else:
        body = (
            f"{assignment.group.name} · {assignment.title} 과제 마감까지 "
            f"{slot.label} 남았습니다."
        )
    return json.dumps(
        {
            "title": "우선콕 마감 알림",
            "body": body,
            "url": f"/groups/{assignment.group_id}/",
            "tag": f"assignment-{assignment.id}",
        },
        ensure_ascii=False,
    )


def send_assignment_notifications(now=None):
    """Send the current due slot once per incomplete user and assignment."""
    if not settings.WEBPUSH_VAPID_PRIVATE_KEY or not settings.WEBPUSH_VAPID_PUBLIC_KEY:
        raise ImproperlyConfigured("자동 푸시 발송에 필요한 VAPID 키가 없습니다.")

    now = now or timezone.now()
    assignments = list(
        Assignment.objects.filter(due_at__lte=now + timedelta(hours=72))
        .select_related("group")
        .order_by("due_at")
    )
    assignment_ids = [assignment.id for assignment in assignments]
    statuses = {
        (row["assignment_id"], row["user_id"]): row["status"]
        for row in AssignmentProgress.objects.filter(
            assignment_id__in=assignment_ids
        ).values("assignment_id", "user_id", "status")
    }

    summary = {"sent_users": 0, "sent_devices": 0, "skipped": 0, "failed": 0}
    for assignment in assignments:
        slot = current_notification_slot(assignment.due_at, now)
        if slot is None:
            continue
        memberships = GroupMembership.objects.filter(
            group_id=assignment.group_id, user__is_active=True
        ).select_related("user")
        for membership in memberships:
            status = statuses.get(
                (assignment.id, membership.user_id), AssignmentProgress.Status.TODO
            )
            if status == AssignmentProgress.Status.DONE:
                summary["skipped"] += 1
                continue

            subscriptions = list(membership.user.push_subscriptions.all())
            if not subscriptions:
                summary["skipped"] += 1
                continue

            with transaction.atomic():
                record, _ = AssignmentNotification.objects.select_for_update().get_or_create(
                    assignment=assignment,
                    user=membership.user,
                    scheduled_for=slot.scheduled_for,
                    defaults={"kind": slot.kind},
                )
                if record.sent_at:
                    summary["skipped"] += 1
                    continue

                sent_devices = 0
                errors = []
                payload = _notification_payload(assignment, slot)
                for subscription in subscriptions:
                    try:
                        webpush(
                            subscription_info=subscription.as_webpush_info(),
                            data=payload,
                            vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
                            vapid_claims={"sub": settings.WEBPUSH_VAPID_SUBJECT},
                        )
                        sent_devices += 1
                    except WebPushException as exc:
                        if exc.response is not None and exc.response.status_code in {404, 410}:
                            subscription.delete()
                        else:
                            errors.append(str(exc))

                record.attempt_count += 1
                record.last_error = "\n".join(errors)[:2000]
                if sent_devices:
                    record.sent_at = now
                    summary["sent_users"] += 1
                    summary["sent_devices"] += sent_devices
                else:
                    summary["failed"] += 1
                record.save(
                    update_fields=["attempt_count", "last_error", "sent_at"]
                )

    return summary
