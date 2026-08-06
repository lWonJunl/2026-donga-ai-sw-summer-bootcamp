import json
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import (
    Assignment,
    AssignmentNotification,
    AssignmentProgress,
    ClassGroup,
    EmailVerification,
    GroupMembership,
    LoginAttempt,
    PeerReminder,
    PushSubscription,
)
from .services import calculate_risk
from .notifications import current_notification_slot, send_assignment_notifications


class RiskCalculationTests(TestCase):
    def test_todo_due_within_three_days_is_warning(self):
        risk = calculate_risk(
            timezone.now() + timedelta(days=2), AssignmentProgress.Status.TODO
        )
        self.assertEqual(risk.level, "warning")

    def test_due_within_24_hours_is_danger(self):
        risk = calculate_risk(
            timezone.now() + timedelta(hours=12), AssignmentProgress.Status.DOING
        )
        self.assertEqual(risk.level, "danger")

    def test_done_assignment_is_safe_even_after_deadline(self):
        risk = calculate_risk(
            timezone.now() - timedelta(days=1), AssignmentProgress.Status.DONE
        )
        self.assertEqual(risk.level, "safe")


class AssignmentNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notify-user", password="test-pass-123"
        )
        self.group = ClassGroup.objects.create(
            name="데이터베이스 스터디",
            description="데이터베이스 과제를 함께 관리합니다.",
            created_by=self.user,
        )
        GroupMembership.objects.create(
            group=self.group,
            user=self.user,
            role=GroupMembership.Role.OWNER,
        )
        PushSubscription.objects.create(
            user=self.user,
            endpoint="https://push.example.test/automatic",
            p256dh="test-p256dh",
            auth="test-auth",
        )

    def test_slot_uses_latest_crossed_pre_due_threshold(self):
        now = timezone.now()
        slot = current_notification_slot(now + timedelta(hours=20), now)

        self.assertEqual(slot.kind, AssignmentNotification.Kind.BEFORE_DUE)
        self.assertEqual(slot.label, "24시간")

    def test_overdue_slot_changes_every_six_hours(self):
        now = timezone.now()
        due_at = now - timedelta(hours=7)
        slot = current_notification_slot(due_at, now)

        self.assertEqual(slot.kind, AssignmentNotification.Kind.OVERDUE)
        self.assertEqual(slot.scheduled_for, due_at + timedelta(hours=6))
        self.assertEqual(slot.label, "마감 6시간 초과")

    @override_settings(
        WEBPUSH_VAPID_PRIVATE_KEY="test-private-key",
        WEBPUSH_VAPID_PUBLIC_KEY="test-public-key",
        WEBPUSH_VAPID_SUBJECT="mailto:test@example.com",
    )
    @patch("tracker.notifications.webpush")
    def test_same_slot_is_sent_only_once(self, mocked_webpush):
        now = timezone.now()
        assignment = Assignment.objects.create(
            group=self.group,
            title="ERD 설계",
            due_at=now + timedelta(hours=20),
            created_by=self.user,
        )

        first = send_assignment_notifications(now)
        second = send_assignment_notifications(now + timedelta(minutes=5))

        self.assertEqual(first["sent_users"], 1)
        self.assertEqual(second["sent_users"], 0)
        self.assertEqual(mocked_webpush.call_count, 1)
        self.assertEqual(
            AssignmentNotification.objects.filter(
                assignment=assignment, user=self.user, sent_at__isnull=False
            ).count(),
            1,
        )

    @override_settings(
        WEBPUSH_VAPID_PRIVATE_KEY="test-private-key",
        WEBPUSH_VAPID_PUBLIC_KEY="test-public-key",
        WEBPUSH_VAPID_SUBJECT="mailto:test@example.com",
    )
    @patch("tracker.notifications.webpush")
    def test_done_assignment_does_not_send(self, mocked_webpush):
        now = timezone.now()
        assignment = Assignment.objects.create(
            group=self.group,
            title="완료한 과제",
            due_at=now + timedelta(hours=20),
            created_by=self.user,
        )
        AssignmentProgress.objects.create(
            assignment=assignment,
            user=self.user,
            status=AssignmentProgress.Status.DONE,
        )

        result = send_assignment_notifications(now)

        self.assertEqual(result["sent_users"], 0)
        mocked_webpush.assert_not_called()
        self.assertFalse(AssignmentNotification.objects.exists())

    @override_settings(
        WEBPUSH_VAPID_PRIVATE_KEY="test-private-key",
        WEBPUSH_VAPID_PUBLIC_KEY="test-public-key",
        WEBPUSH_VAPID_SUBJECT="mailto:test@example.com",
    )
    @patch("tracker.notifications.webpush")
    def test_overdue_assignment_sends_again_in_next_six_hour_slot(
        self, mocked_webpush
    ):
        due_at = timezone.now() - timedelta(minutes=5)
        assignment = Assignment.objects.create(
            group=self.group,
            title="마감 초과 과제",
            due_at=due_at,
            created_by=self.user,
        )

        send_assignment_notifications(due_at + timedelta(minutes=5))
        send_assignment_notifications(due_at + timedelta(hours=6, minutes=5))

        self.assertEqual(mocked_webpush.call_count, 2)
        self.assertEqual(
            AssignmentNotification.objects.filter(assignment=assignment).count(), 2
        )


class CollaborationTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            "owner", email="owner@example.com", password="test-pass-123"
        )
        self.friend = User.objects.create_user(
            "friend", email="friend@example.com", password="test-pass-123"
        )
        self.outsider = User.objects.create_user(
            "outsider", email="outsider@example.com", password="test-pass-123"
        )
        self.group = ClassGroup.objects.create(
            name="자료구조 스터디",
            description="자료구조 과제와 일정을 함께 관리합니다.",
            created_by=self.owner,
        )
        GroupMembership.objects.create(
            group=self.group, user=self.owner, role=GroupMembership.Role.OWNER
        )
        self.assignment = Assignment.objects.create(
            group=self.group,
            title="연결 리스트 구현",
            due_at=timezone.now() + timedelta(days=2),
            created_by=self.owner,
        )

    def test_friend_can_join_with_invite_code(self):
        self.client.force_login(self.friend)
        response = self.client.post(
            reverse("join_group"), {"invite_code": self.group.invite_code.lower()}
        )
        self.assertRedirects(response, reverse("group_detail", args=[self.group.id]))
        self.assertTrue(
            GroupMembership.objects.filter(group=self.group, user=self.friend).exists()
        )

    def test_group_required_fields_are_validated(self):
        self.client.force_login(self.owner)
        before_count = ClassGroup.objects.count()

        response = self.client.post(
            reverse("create_group"),
            {
                "name": "",
                "description": "설명만 입력",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ClassGroup.objects.count(), before_count)
        form = response.context["form"]
        self.assertFormError(form, "name", "필수 항목입니다.")

    def test_landing_and_login_flow(self):
        landing_response = self.client.get(reverse("landing"))
        self.assertEqual(landing_response.status_code, 200)
        self.assertContains(landing_response, "로그인하고 시작하기")

        login_response = self.client.post(
            reverse("login"),
            {"username": "owner@example.com", "password": "test-pass-123"},
        )
        self.assertRedirects(login_response, reverse("dashboard"))

        authenticated_landing = self.client.get(reverse("landing"))
        self.assertRedirects(authenticated_landing, reverse("dashboard"))

        logout_response = self.client.post(reverse("logout"))
        self.assertRedirects(logout_response, reverse("landing"))

    def test_auth_pages_render(self):
        login_response = self.client.get(reverse("login"))
        signup_response = self.client.get(reverse("signup"))

        self.assertContains(login_response, "내 과제 현황을")
        self.assertContains(login_response, "로그인", count=4)
        self.assertContains(signup_response, "과제 관리를")
        self.assertContains(signup_response, "계정 만들기")

    @override_settings(
        REFRESH_RATE_LIMIT_REQUESTS=3,
        REFRESH_RATE_LIMIT_WINDOW_SECONDS=10,
        REFRESH_RATE_LIMIT_BLOCK_SECONDS=30,
    )
    def test_repeated_refresh_is_blocked_for_30_seconds(self):
        cache.clear()
        remote_address = "198.51.100.7"
        for _ in range(3):
            response = self.client.get(
                reverse("landing"), REMOTE_ADDR=remote_address
            )
            self.assertEqual(response.status_code, 200)

        blocked_response = self.client.get(
            reverse("landing"), REMOTE_ADDR=remote_address
        )
        self.assertEqual(blocked_response.status_code, 429)
        self.assertEqual(blocked_response["Retry-After"], "30")
        self.assertContains(
            blocked_response, "반복적인 새로고침이 감지", status_code=429
        )
        cache.clear()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_signup_requires_email_verification(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "new-user",
                "email": "new@example.com",
                "password1": "new-test-pass-123",
                "password2": "new-test-pass-123",
            },
        )
        user = User.objects.get(username="new-user")
        self.assertFalse(user.is_active)
        self.assertContains(response, "인증 메일을 보냈습니다")
        self.assertEqual(len(mail.outbox), 1)

        login_response = self.client.post(
            reverse("login"),
            {"username": "new@example.com", "password": "new-test-pass-123"},
        )
        self.assertContains(login_response, "이메일 인증이 필요합니다")

        verification = user.email_verification
        verify_response = self.client.get(
            reverse("verify_email", args=[verification.token])
        )
        self.assertRedirects(verify_response, reverse("login"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        SITE_URL="https://assignments.example.test",
        ALLOWED_HOSTS=["attacker.example"],
    )
    def test_signup_email_uses_configured_site_url(self):
        self.client.post(
            reverse("signup"),
            {
                "username": "site-url-user",
                "email": "site-url@example.com",
                "password1": "strong-test-pass-8472",
                "password2": "strong-test-pass-8472",
            },
            HTTP_HOST="attacker.example",
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("https://assignments.example.test/accounts/verify/", mail.outbox[0].body)
        self.assertNotIn("attacker.example", mail.outbox[0].body)

    @override_settings(EMAIL_VERIFICATION_MAX_AGE_SECONDS=60)
    def test_expired_email_verification_is_rejected(self):
        user = User.objects.create_user(
            "expired-user", email="expired@example.com", password="strong-pass-8472"
        )
        user.is_active = False
        user.save(update_fields=["is_active"])
        verification = EmailVerification.objects.create(user=user)
        EmailVerification.objects.filter(pk=verification.pk).update(
            created_at=timezone.now() - timedelta(minutes=2)
        )

        response = self.client.get(
            reverse("verify_email", args=[verification.token])
        )

        self.assertRedirects(response, reverse("signup"))
        self.assertFalse(User.objects.filter(pk=user.pk).exists())

    @override_settings(
        SENSITIVE_POST_RATE_LIMIT_REQUESTS=1,
        SENSITIVE_POST_RATE_LIMIT_WINDOW_SECONDS=60,
    )
    def test_sensitive_post_requests_are_rate_limited(self):
        cache.clear()
        self.client.force_login(self.owner)
        first = self.client.post(reverse("join_group"), {"invite_code": "INVALID1"})
        second = self.client.post(reverse("join_group"), {"invite_code": "INVALID2"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        cache.clear()

    def test_authenticated_user_can_change_password(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("password_change"),
            {
                "old_password": "test-pass-123",
                "new_password1": "changed-test-pass-456",
                "new_password2": "changed-test-pass-456",
            },
        )
        self.assertRedirects(response, reverse("password_change_done"))
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password("changed-test-pass-456"))

    def test_login_is_locked_for_30_seconds_after_five_failures(self):
        for _ in range(4):
            response = self.client.post(
                reverse("login"),
                {"username": "owner@example.com", "password": "wrong-password"},
            )
            self.assertNotContains(response, "30초 후 다시 시도")

        response = self.client.post(
            reverse("login"),
            {"username": "owner@example.com", "password": "wrong-password"},
        )
        self.assertContains(response, "30초 후 다시 시도")

        locked_response = self.client.post(
            reverse("login"),
            {"username": "owner@example.com", "password": "test-pass-123"},
        )
        self.assertContains(locked_response, "30초 후 다시 시도")
        self.assertNotIn("_auth_user_id", self.client.session)

        attempt = LoginAttempt.objects.get(
            identifier="owner@example.com:127.0.0.1"
        )
        attempt.locked_until = timezone.now() - timedelta(seconds=1)
        attempt.save(update_fields=["locked_until"])
        unlocked_response = self.client.post(
            reverse("login"),
            {"username": "owner@example.com", "password": "test-pass-123"},
        )
        self.assertRedirects(unlocked_response, reverse("dashboard"))
        self.assertFalse(LoginAttempt.objects.filter(identifier=attempt.identifier).exists())

    def test_account_delete_is_blocked_for_sole_group_owner(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("delete_account"), {"password": "test-pass-123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "단독 관리자인 그룹이 있습니다")
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.is_active)

    def test_account_can_be_anonymized_after_another_owner_is_assigned(self):
        GroupMembership.objects.create(
            group=self.group,
            user=self.friend,
            role=GroupMembership.Role.OWNER,
        )
        owner_id = self.owner.id
        assignment_id = self.assignment.id
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("delete_account"), {"password": "test-pass-123"}
        )

        self.assertRedirects(response, reverse("landing"))
        deleted_user = User.objects.get(id=owner_id)
        self.assertFalse(deleted_user.is_active)
        self.assertEqual(deleted_user.username, f"deleted-user-{owner_id}")
        self.assertEqual(deleted_user.email, "")
        self.assertFalse(
            GroupMembership.objects.filter(user_id=owner_id).exists()
        )
        self.assertTrue(Assignment.objects.filter(id=assignment_id).exists())

    def test_user_can_save_and_delete_push_subscription(self):
        self.client.force_login(self.owner)
        subscription = {
            "endpoint": "https://push.example.test/subscription-1",
            "keys": {"p256dh": "test-p256dh", "auth": "test-auth"},
        }
        save_response = self.client.post(
            reverse("push_subscribe"),
            data=json.dumps(subscription),
            content_type="application/json",
        )
        self.assertEqual(save_response.status_code, 200)
        self.assertTrue(
            PushSubscription.objects.filter(
                user=self.owner, endpoint=subscription["endpoint"]
            ).exists()
        )

        delete_response = self.client.post(
            reverse("push_unsubscribe"),
            data=json.dumps({"endpoint": subscription["endpoint"]}),
            content_type="application/json",
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(
            PushSubscription.objects.filter(endpoint=subscription["endpoint"]).exists()
        )

    def test_member_can_open_dashboard_and_group_page(self):
        self.assignment.description = "과제 설명 확인용"
        self.assignment.save(update_fields=["description"])
        self.client.force_login(self.owner)
        dashboard_response = self.client.get(reverse("dashboard"))
        group_response = self.client.get(reverse("group_detail", args=[self.group.id]))

        self.assertContains(dashboard_response, "연결 리스트 구현")
        self.assertContains(dashboard_response, "과제 설명 확인용")
        self.assertContains(group_response, self.group.invite_code)

    def test_member_can_open_guide(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("guide"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "위험도 기준")
        self.assertContains(response, "72시간")

    def test_member_can_open_my_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("my_page"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.owner.username)
        self.assertContains(response, "로그아웃")

    def test_my_page_active_count_uses_only_current_users_progress(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.friend,
            status=AssignmentProgress.Status.DONE,
        )
        self.client.force_login(self.owner)

        response = self.client.get(reverse("my_page"))
        self.assertEqual(response.context["active_assignment_count"], 1)

        AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.owner,
            status=AssignmentProgress.Status.DONE,
        )
        response = self.client.get(reverse("my_page"))
        self.assertEqual(response.context["active_assignment_count"], 0)

    def test_member_can_open_courses_page(self):
        self.group.description = "전공 필수 과제를 함께 관리합니다."
        self.group.save(update_fields=["description"])
        self.client.force_login(self.owner)
        response = self.client.get(reverse("courses"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group.name)
        self.assertContains(response, self.group.description)
        self.assertContains(response, "카드형")
        self.assertContains(response, "목록형")
        self.assertContains(response, "data-course-collection")

    def test_done_assignment_is_hidden_from_dashboard(self):
        AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.owner,
            status=AssignmentProgress.Status.DONE,
        )
        self.client.force_login(self.owner)

        dashboard_response = self.client.get(reverse("dashboard"))
        group_response = self.client.get(
            reverse("group_detail", args=[self.group.id])
        )

        self.assertNotContains(dashboard_response, self.assignment.title)
        self.assertContains(dashboard_response, "등록된 과제 1개를 모두 완료했습니다")
        self.assertContains(group_response, self.assignment.title)

    def test_outsider_cannot_open_group(self):
        self.client.force_login(self.outsider)
        response = self.client.get(reverse("group_detail", args=[self.group.id]))
        self.assertEqual(response.status_code, 404)

    def test_progress_is_saved_for_each_user(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.owner,
            status=AssignmentProgress.Status.DONE,
        )

        self.client.force_login(self.friend)
        self.client.post(
            reverse("update_progress", args=[self.assignment.id]),
            {"status": AssignmentProgress.Status.DOING},
        )

        owner_progress = AssignmentProgress.objects.get(
            assignment=self.assignment, user=self.owner
        )
        friend_progress = AssignmentProgress.objects.get(
            assignment=self.assignment, user=self.friend
        )
        self.assertEqual(owner_progress.status, AssignmentProgress.Status.DONE)
        self.assertEqual(friend_progress.status, AssignmentProgress.Status.DOING)

    @override_settings(
        WEBPUSH_VAPID_PRIVATE_KEY="test-private-key",
        WEBPUSH_VAPID_PUBLIC_KEY="test-public-key",
        WEBPUSH_VAPID_SUBJECT="mailto:test@example.com",
    )
    @patch("tracker.views.webpush")
    def test_shared_progress_and_peer_reminder(self, mocked_webpush):
        self.group.show_member_progress = True
        self.group.save(update_fields=["show_member_progress"])
        GroupMembership.objects.create(group=self.group, user=self.friend)
        AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.friend,
            status=AssignmentProgress.Status.DOING,
        )
        PushSubscription.objects.create(
            user=self.friend,
            endpoint="https://push.example.test/friend",
            p256dh="friend-p256dh",
            auth="friend-auth",
        )
        self.client.force_login(self.owner)

        page = self.client.get(reverse("group_detail", args=[self.group.id]))
        self.assertContains(page, "미완료 구성원 보기")
        self.assertContains(page, "1개 미완료")
        self.assertContains(page, "구성원 현황")
        self.assertContains(page, self.friend.username)
        self.assertContains(page, "진행 중")
        self.assertContains(page, "👉")
        self.assertContains(page, "찌르기")
        friend_summary = next(
            item
            for item in page.context["incomplete_members"]
            if item["membership"].user_id == self.friend.id
        )
        self.assertEqual(len(friend_summary["assignments"]), 1)
        self.assertEqual(
            friend_summary["assignments"][0]["status"],
            AssignmentProgress.Status.DOING,
        )

        response = self.client.post(
            reverse("send_peer_reminder", args=[self.assignment.id, self.friend.id])
        )
        self.assertRedirects(response, reverse("group_detail", args=[self.group.id]))
        self.assertEqual(mocked_webpush.call_count, 1)
        payload = json.loads(mocked_webpush.call_args.kwargs["data"])
        self.assertEqual(
            payload["body"],
            "누군가가 당신에게 ‘연결 리스트 구현’을 하라고 찔렀습니다.",
        )
        self.assertTrue(
            PeerReminder.objects.filter(
                assignment=self.assignment,
                sender=self.owner,
                recipient=self.friend,
                delivered_count=1,
            ).exists()
        )

    @override_settings(
        WEBPUSH_VAPID_PRIVATE_KEY="test-private-key",
        WEBPUSH_VAPID_PUBLIC_KEY="test-public-key",
        WEBPUSH_VAPID_SUBJECT="mailto:test@example.com",
    )
    @patch("tracker.views.webpush")
    def test_peer_reminder_is_limited_to_once_per_30_minutes(self, mocked_webpush):
        self.group.show_member_progress = True
        self.group.save(update_fields=["show_member_progress"])
        GroupMembership.objects.create(group=self.group, user=self.friend)
        PeerReminder.objects.create(
            assignment=self.assignment,
            sender=self.owner,
            recipient=self.friend,
            delivered_count=1,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("send_peer_reminder", args=[self.assignment.id, self.friend.id])
        )

        self.assertRedirects(response, reverse("group_detail", args=[self.group.id]))
        self.assertEqual(PeerReminder.objects.count(), 1)
        mocked_webpush.assert_not_called()

    def test_peer_reminder_requires_shared_progress_option(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("send_peer_reminder", args=[self.assignment.id, self.friend.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(PeerReminder.objects.exists())

    def test_completed_member_cannot_be_reminded(self):
        self.group.show_member_progress = True
        self.group.save(update_fields=["show_member_progress"])
        GroupMembership.objects.create(group=self.group, user=self.friend)
        AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.friend,
            status=AssignmentProgress.Status.DONE,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("send_peer_reminder", args=[self.assignment.id, self.friend.id])
        )

        self.assertRedirects(response, reverse("group_detail", args=[self.group.id]))
        self.assertFalse(PeerReminder.objects.exists())

    def test_member_can_add_shared_assignment(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        self.client.force_login(self.friend)
        response = self.client.post(
            reverse("create_assignment", args=[self.group.id]),
            {
                "title": "스택 보고서",
                "description": "PDF로 제출",
                "due_at": (timezone.now() + timedelta(days=5)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
        )
        self.assertRedirects(response, reverse("group_detail", args=[self.group.id]))
        self.assertTrue(
            Assignment.objects.filter(group=self.group, title="스택 보고서").exists()
        )

    def test_assignment_title_and_due_date_are_required(self):
        self.client.force_login(self.owner)
        before_count = Assignment.objects.count()
        response = self.client.post(
            reverse("create_assignment", args=[self.group.id]),
            {"title": "", "description": "선택 설명", "due_at": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Assignment.objects.count(), before_count)
        form = response.context["form"]
        self.assertFormError(form, "title", "필수 항목입니다.")
        self.assertFormError(form, "due_at", "필수 항목입니다.")

    def test_owner_can_manage_member_role_and_remove_member(self):
        membership = GroupMembership.objects.create(
            group=self.group, user=self.friend
        )
        self.client.force_login(self.owner)

        promote_response = self.client.post(
            reverse("manage_member", args=[membership.id]),
            {"action": "make_owner"},
        )
        self.assertRedirects(
            promote_response, reverse("group_manage", args=[self.group.id])
        )
        membership.refresh_from_db()
        self.assertEqual(membership.role, GroupMembership.Role.OWNER)

        remove_response = self.client.post(
            reverse("manage_member", args=[membership.id]),
            {"action": "remove"},
        )
        self.assertRedirects(
            remove_response, reverse("group_manage", args=[self.group.id])
        )
        self.assertFalse(GroupMembership.objects.filter(id=membership.id).exists())

    def test_owner_can_edit_and_delete_assignment(self):
        self.client.force_login(self.owner)
        edit_response = self.client.post(
            reverse("edit_assignment", args=[self.assignment.id]),
            {
                "title": "수정된 과제",
                "description": "관리자가 수정함",
                "due_at": (timezone.now() + timedelta(days=4)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
        )
        self.assertRedirects(
            edit_response, reverse("group_detail", args=[self.group.id])
        )
        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.title, "수정된 과제")

        delete_response = self.client.post(
            reverse("delete_assignment", args=[self.assignment.id])
        )
        self.assertRedirects(
            delete_response, reverse("group_detail", args=[self.group.id])
        )
        self.assertFalse(Assignment.objects.filter(id=self.assignment.id).exists())

    def test_member_cannot_use_owner_management_actions(self):
        membership = GroupMembership.objects.create(
            group=self.group, user=self.friend
        )
        self.client.force_login(self.friend)

        edit_response = self.client.get(
            reverse("edit_assignment", args=[self.assignment.id])
        )
        delete_response = self.client.post(
            reverse("delete_assignment", args=[self.assignment.id])
        )
        manage_response = self.client.post(
            reverse("manage_member", args=[membership.id]),
            {"action": "make_owner"},
        )

        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)
        self.assertEqual(manage_response.status_code, 403)
        self.assertTrue(Assignment.objects.filter(id=self.assignment.id).exists())

    def test_member_can_edit_and_delete_assignment_they_created(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        member_assignment = Assignment.objects.create(
            group=self.group,
            title="구성원이 등록한 과제",
            due_at=timezone.now() + timedelta(days=5),
            created_by=self.friend,
        )
        self.client.force_login(self.friend)

        edit_response = self.client.post(
            reverse("edit_assignment", args=[member_assignment.id]),
            {
                "title": "구성원이 수정한 과제",
                "description": "직접 수정",
                "due_at": (timezone.now() + timedelta(days=6)).strftime(
                    "%Y-%m-%dT%H:%M"
                ),
            },
        )
        self.assertRedirects(
            edit_response, reverse("group_detail", args=[self.group.id])
        )
        member_assignment.refresh_from_db()
        self.assertEqual(member_assignment.title, "구성원이 수정한 과제")

        delete_response = self.client.post(
            reverse("delete_assignment", args=[member_assignment.id])
        )
        self.assertRedirects(
            delete_response, reverse("group_detail", args=[self.group.id])
        )
        self.assertFalse(Assignment.objects.filter(id=member_assignment.id).exists())

    def test_owner_can_delete_assignment_created_by_member(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        member_assignment = Assignment.objects.create(
            group=self.group,
            title="구성원이 등록한 과제",
            due_at=timezone.now() + timedelta(days=5),
            created_by=self.friend,
        )
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("delete_assignment", args=[member_assignment.id])
        )

        self.assertRedirects(response, reverse("group_detail", args=[self.group.id]))
        self.assertFalse(Assignment.objects.filter(id=member_assignment.id).exists())

    def test_last_owner_cannot_be_demoted(self):
        owner_membership = GroupMembership.objects.get(
            group=self.group, user=self.owner
        )
        self.client.force_login(self.owner)
        self.client.post(
            reverse("manage_member", args=[owner_membership.id]),
            {"action": "make_member"},
        )

        owner_membership.refresh_from_db()
        self.assertEqual(owner_membership.role, GroupMembership.Role.OWNER)

    def test_owner_can_delete_group_with_group_name_confirmation(self):
        group_id = self.group.id
        assignment_id = self.assignment.id
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("delete_group", args=[group_id]),
            {"confirmation": self.group.name},
        )

        self.assertRedirects(response, reverse("courses"))
        self.assertFalse(ClassGroup.objects.filter(id=group_id).exists())
        self.assertFalse(Assignment.objects.filter(id=assignment_id).exists())

    def test_member_cannot_delete_group(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        self.client.force_login(self.friend)

        response = self.client.post(
            reverse("delete_group", args=[self.group.id]),
            {"confirmation": self.group.name},
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(ClassGroup.objects.filter(id=self.group.id).exists())

    def test_group_delete_requires_exact_group_name(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("delete_group", args=[self.group.id]),
            {"confirmation": "잘못된 그룹 이름"},
        )

        self.assertRedirects(
            response, reverse("group_manage", args=[self.group.id])
        )
        self.assertTrue(ClassGroup.objects.filter(id=self.group.id).exists())

    def test_group_management_page_is_owner_only(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)

        self.client.force_login(self.owner)
        owner_response = self.client.get(
            reverse("group_manage", args=[self.group.id])
        )
        self.assertEqual(owner_response.status_code, 200)
        self.assertContains(owner_response, "구성원 관리")
        self.assertContains(owner_response, "그룹 삭제")

        self.client.force_login(self.friend)
        member_response = self.client.get(
            reverse("group_manage", args=[self.group.id])
        )
        self.assertEqual(member_response.status_code, 403)

    def test_member_can_leave_group_and_personal_progress_is_deleted(self):
        membership = GroupMembership.objects.create(
            group=self.group, user=self.friend
        )
        progress = AssignmentProgress.objects.create(
            assignment=self.assignment,
            user=self.friend,
            status=AssignmentProgress.Status.DOING,
        )
        self.client.force_login(self.friend)

        response = self.client.post(
            reverse("leave_group", args=[self.group.id])
        )

        self.assertRedirects(response, reverse("courses"))
        self.assertFalse(
            GroupMembership.objects.filter(id=membership.id).exists()
        )
        self.assertFalse(
            AssignmentProgress.objects.filter(id=progress.id).exists()
        )

    def test_sole_owner_cannot_leave_group(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("leave_group", args=[self.group.id])
        )

        self.assertRedirects(
            response, reverse("group_detail", args=[self.group.id])
        )
        self.assertTrue(
            GroupMembership.objects.filter(
                group=self.group,
                user=self.owner,
                role=GroupMembership.Role.OWNER,
            ).exists()
        )

    def test_owner_can_edit_group_information_but_member_cannot(self):
        GroupMembership.objects.create(group=self.group, user=self.friend)
        invite_code = self.group.invite_code
        payload = {
            "name": "알고리즘 팀",
            "description": "알고리즘 과제와 팀 일정을 함께 관리합니다.",
        }

        self.client.force_login(self.owner)
        owner_response = self.client.post(
            reverse("edit_group", args=[self.group.id]), payload
        )
        self.assertRedirects(
            owner_response, reverse("group_manage", args=[self.group.id])
        )
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, "알고리즘 팀")
        self.assertEqual(
            self.group.description,
            "알고리즘 과제와 팀 일정을 함께 관리합니다.",
        )
        self.assertEqual(self.group.invite_code, invite_code)

        self.client.force_login(self.friend)
        member_response = self.client.get(
            reverse("edit_group", args=[self.group.id])
        )
        self.assertEqual(member_response.status_code, 403)
