import re

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core.cache import cache
from django.core import mail


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        cache.clear()

    def create_verified_user(self, username="verified_user", email="verified@example.com"):
        user = get_user_model().objects.create_user(
            username=username,
            email=email,
            password="Test-password-4826",
        )
        EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
        return user

    def test_registration_requires_email_verification(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "portfolio_user",
                "email": "portfolio@example.com",
                "password1": "Test-password-4826",
                "password2": "Test-password-4826",
                "next": reverse("api_page"),
            },
        )
        self.assertRedirects(response, reverse("account_email_verification_sent"))
        address = EmailAddress.objects.get(email="portfolio@example.com")
        self.assertFalse(address.verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.client.get(reverse("api_portfolio"), HTTP_ACCEPT="application/json").status_code,
            401,
        )

    def test_unverified_user_cannot_log_in(self):
        user = get_user_model().objects.create_user(
            username="pending", email="pending@example.com", password="Test-password-4826"
        )
        EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
        response = self.client.post(
            reverse("login"), {"username": user.username, "password": "Test-password-4826"}
        )
        self.assertContains(response, "이메일 인증을 완료한 후 로그인해 주세요")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_email_confirmation_marks_address_verified(self):
        self.client.post(
            reverse("register"),
            {
                "username": "confirm_user",
                "email": "confirm@example.com",
                "password1": "Test-password-4826",
                "password2": "Test-password-4826",
            },
        )
        match = re.search(r"https?://[^/]+(/accounts/confirm-email/[^/\s]+/)", mail.outbox[0].body)
        self.assertIsNotNone(match)
        confirmation_url = match.group(1)
        self.client.get(confirmation_url)
        response = self.client.post(confirmation_url)
        self.assertTrue(
            EmailAddress.objects.get(email="confirm@example.com").verified,
            msg=f"confirmation returned HTTP {response.status_code} for {confirmation_url}",
        )

    def test_reserved_username_is_rejected(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "NULL",
                "email": "null@example.com",
                "password1": "Test-password-4826",
                "password2": "Test-password-4826",
            },
        )
        self.assertContains(response, "사용할 수 없는 아이디입니다")
        self.assertFalse(get_user_model().objects.filter(username__iexact="null").exists())

    def test_anonymous_user_cannot_read_protected_api(self):
        response = self.client.get(reverse("api_projects"), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["login_url"], reverse("login"))

    def test_anonymous_browser_is_warned_on_login_page(self):
        response = self.client.get(reverse("api_projects"), HTTP_ACCEPT="text/html")
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=%2Fapi%2Fprojects%2F&reason=authentication_required",
            fetch_redirect_response=False,
        )

        login_page = self.client.get(response.url)
        self.assertContains(login_page, "로그인이 필요한 서비스입니다")

    def test_api_page_is_public(self):
        response = self.client.get(reverse("api_page"))
        self.assertEqual(response.status_code, 200)

    def test_old_registration_redirect_goes_to_login_warning(self):
        response = self.client.get(
            reverse("register"),
            {"next": reverse("api_project_detail", args=[1])},
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next=%2Fapi%2Fprojects%2F1%2F&reason=authentication_required",
            fetch_redirect_response=False,
        )

    def test_explicit_registration_choice_opens_registration_page(self):
        response = self.client.get(
            reverse("register"),
            {"next": reverse("api_page"), "intent": "register"},
        )
        self.assertEqual(response.status_code, 200)

    def test_security_headers_are_set(self):
        response = self.client.get(reverse("api_page"))
        self.assertIn("default-src 'self'", response["Content-Security-Policy"])
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertIn("camera=()", response["Permissions-Policy"])

    def test_authenticated_api_is_not_cacheable(self):
        self.client.force_login(self.create_verified_user("cache_user", "cache@example.com"))
        response = self.client.get(reverse("api_portfolio"))
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertIn("Cookie", response["Vary"])

    def test_repeated_failed_logins_are_rate_limited(self):
        payload = {"username": "missing", "password": "wrong-password"}
        for _ in range(5):
            self.client.post(reverse("login"), payload)
        response = self.client.post(reverse("login"), payload)
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "로그인 시도가 너무 많습니다", status_code=429)

    def test_logout_locks_api_again(self):
        self.client.force_login(self.create_verified_user("logout_user", "logout@example.com"))
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("api_projects"), HTTP_ACCEPT="application/json").status_code, 401)

    def test_logout_requires_post(self):
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

    def test_profile_can_update_user_information(self):
        user = self.create_verified_user("profile_user", "profile@example.com")
        self.client.force_login(user)
        response = self.client.post(
            reverse("profile"),
            {"username": "updated_user", "first_name": "Won", "last_name": "Jun"},
        )
        self.assertRedirects(response, reverse("profile"))
        user.refresh_from_db()
        self.assertEqual(user.username, "updated_user")
        self.assertEqual(user.first_name, "Won")

    def test_password_reset_sends_email_without_revealing_account(self):
        self.create_verified_user("reset_user", "reset@example.com")
        response = self.client.post(
            reverse("account_reset_password"), {"email": "reset@example.com"}
        )
        self.assertRedirects(response, reverse("account_reset_password_done"))
        self.assertEqual(len(mail.outbox), 1)
