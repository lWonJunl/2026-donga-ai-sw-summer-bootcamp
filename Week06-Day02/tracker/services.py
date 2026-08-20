from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from .models import AssignmentProgress


@dataclass(frozen=True)
class Risk:
    level: str
    label: str
    message: str
    rank: int


def calculate_risk(due_at, status):
    if status == AssignmentProgress.Status.DONE:
        return Risk("safe", "안전", "완료한 과제", 3)

    remaining = due_at - timezone.now()
    if remaining.total_seconds() < 0:
        return Risk("overdue", "마감 초과", "제출 기한이 지났습니다", 0)

    if remaining <= timedelta(hours=24):
        return Risk("danger", "위험", "24시간 이내 마감", 1)

    if remaining <= timedelta(days=3):
        return Risk("warning", "주의", "72시간 이내 마감", 2)

    return Risk("safe", "여유", "마감까지 여유 있음", 3)


def remaining_text(due_at):
    seconds = int((due_at - timezone.now()).total_seconds())
    if seconds < 0:
        overdue_seconds = abs(seconds)
        days = overdue_seconds // 86400
        return f"마감 {days}일 지남" if days else "마감 시간이 지남"

    days, rest = divmod(seconds, 86400)
    hours = rest // 3600
    if days:
        return f"{days}일 {hours}시간 남음"
    minutes = max(0, (rest % 3600) // 60)
    return f"{hours}시간 {minutes}분 남음"
