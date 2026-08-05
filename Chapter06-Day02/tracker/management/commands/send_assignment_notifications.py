from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured

from tracker.notifications import send_assignment_notifications


class Command(BaseCommand):
    help = "마감 시점에 해당하는 미완료 과제의 브라우저 푸시 알림을 발송합니다."

    def handle(self, *args, **options):
        try:
            summary = send_assignment_notifications()
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                "자동 알림 처리 완료: "
                f"사용자 {summary['sent_users']}명, "
                f"기기 {summary['sent_devices']}대 발송, "
                f"건너뜀 {summary['skipped']}건, 실패 {summary['failed']}건"
            )
        )
