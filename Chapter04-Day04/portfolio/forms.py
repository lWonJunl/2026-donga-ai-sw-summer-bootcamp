import unicodedata

from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model


RESERVED_USERNAMES = {
    "null", "none", "nil", "undefined", "nan", "true", "false",
    "admin", "administrator", "root", "system", "api", "login",
    "logout", "register", "account", "accounts", "me", "user",
}


def validate_safe_username(value, current_user=None):
    username = unicodedata.normalize("NFKC", value).strip()
    if username.casefold() in RESERVED_USERNAMES:
        raise forms.ValidationError("사용할 수 없는 아이디입니다. 다른 아이디를 입력해 주세요.")
    users = get_user_model().objects.filter(username__iexact=username)
    if current_user is not None:
        users = users.exclude(pk=current_user.pk)
    if users.exists():
        raise forms.ValidationError("사용할 수 없는 아이디입니다. 다른 아이디를 입력해 주세요.")
    return username


class SecureSignupForm(SignupForm):
    email = forms.EmailField(label="이메일", required=True)

    def clean_username(self):
        username = super().clean_username()
        return validate_safe_username(username)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "first_name", "last_name"]
        labels = {"username": "아이디", "first_name": "이름", "last_name": "성"}

    def clean_username(self):
        return validate_safe_username(self.cleaned_data["username"], self.instance)
