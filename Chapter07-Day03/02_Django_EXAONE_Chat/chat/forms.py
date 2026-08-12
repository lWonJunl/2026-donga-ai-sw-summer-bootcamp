from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserPreference


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="이메일")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        labels = {"username": "아이디"}


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ("system_prompt",)
        labels = {"system_prompt": "AI 응답 방식"}
        widgets = {
            "system_prompt": forms.Textarea(
                attrs={
                    "rows": 7,
                    "maxlength": 1000,
                    "placeholder": "예: 초보자도 이해할 수 있도록 한국어로 쉽게 설명하고, 필요하면 예제를 보여주세요.",
                }
            ),
        }
