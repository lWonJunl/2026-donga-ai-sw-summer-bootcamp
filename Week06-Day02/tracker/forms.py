from datetime import timedelta

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Assignment, AssignmentProgress, ClassGroup, LoginAttempt


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="이메일",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "autofocus": True}),
    )
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "이메일 또는 비밀번호가 올바르지 않습니다.",
        "email_unverified": "이메일 인증이 필요합니다. 가입 시 받은 인증 메일을 확인해 주세요.",
        "temporarily_locked": "로그인 시도가 너무 많습니다. 30초 후 다시 시도해 주세요.",
    }

    max_failures = 5
    lock_duration = timedelta(seconds=30)

    def throttle_identifier(self, username):
        client_ip = self.request.META.get("REMOTE_ADDR", "unknown")
        return f"{username.strip().lower()}:{client_ip}"

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            account = User.objects.filter(email__iexact=email).first()
            identifier = self.throttle_identifier(email)
            attempt = LoginAttempt.objects.filter(identifier=identifier).first()
            if attempt and attempt.locked_until and attempt.locked_until > timezone.now():
                raise forms.ValidationError(
                    self.error_messages["temporarily_locked"],
                    code="temporarily_locked",
                )
            self.user_cache = authenticate(
                self.request,
                username=account.username if account else email,
                password=password,
            )
            if self.user_cache is None:
                inactive_user = account if account and not account.is_active else None
                if inactive_user and inactive_user.check_password(password):
                    raise forms.ValidationError(
                        self.error_messages["email_unverified"],
                        code="email_unverified",
                    )
                attempt, _ = LoginAttempt.objects.get_or_create(identifier=identifier)
                attempt.failure_count += 1
                if attempt.failure_count >= self.max_failures:
                    attempt.locked_until = timezone.now() + self.lock_duration
                attempt.save(update_fields=["failure_count", "locked_until", "updated_at"])
                if attempt.locked_until:
                    raise forms.ValidationError(
                        self.error_messages["temporarily_locked"],
                        code="temporarily_locked",
                    )
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
            LoginAttempt.objects.filter(identifier=identifier).delete()

        return self.cleaned_data


class AccountDeleteForm(forms.Form):
    password = forms.CharField(
        label="현재 비밀번호",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class SignupForm(UserCreationForm):
    email = forms.EmailField(label="이메일", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email


class ClassGroupForm(forms.ModelForm):
    required_css_class = "required-field"

    class Meta:
        model = ClassGroup
        fields = (
            "name",
            "description",
            "show_member_progress",
        )
        labels = {
            "description": "그룹 설명 (선택)",
            "show_member_progress": "구성원 진행 상태 공개",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 4, "placeholder": "그룹의 목적이나 함께 관리할 내용을 적어 주세요."}
            )
        }


class JoinGroupForm(forms.Form):
    invite_code = forms.CharField(label="초대 코드", max_length=8)

    def clean_invite_code(self):
        return self.cleaned_data["invite_code"].strip().upper()


class AssignmentForm(forms.ModelForm):
    required_css_class = "required-field"

    class Meta:
        model = Assignment
        fields = ("title", "description", "due_at")
        labels = {"description": "설명 (선택)"}
        widgets = {
            "due_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_at"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean_due_at(self):
        due_at = self.cleaned_data["due_at"]
        if due_at <= timezone.now():
            raise forms.ValidationError("현재보다 이후의 마감 시간을 입력하세요.")
        return due_at


class ProgressForm(forms.ModelForm):
    class Meta:
        model = AssignmentProgress
        fields = ("status",)
