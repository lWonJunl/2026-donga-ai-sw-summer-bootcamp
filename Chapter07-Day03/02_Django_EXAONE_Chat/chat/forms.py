from django.conf import settings
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
    system_prompt = forms.CharField(
        label="AI 응답 방식",
        max_length=settings.SYSTEM_PROMPT_MAX_LENGTH,
        widget=forms.Textarea(
            attrs={
                "rows": 7,
                "placeholder": "예: 초보자도 이해할 수 있도록 한국어로 쉽게 설명하고, 필요하면 예제를 보여주세요.",
            }
        ),
    )

    class Meta:
        model = UserPreference
        fields = ("system_prompt",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.fields["system_prompt"]
        field.max_length = settings.SYSTEM_PROMPT_MAX_LENGTH
        field.widget.attrs["maxlength"] = settings.SYSTEM_PROMPT_MAX_LENGTH

    def clean_system_prompt(self):
        value = self.cleaned_data["system_prompt"]
        if len(value) > settings.SYSTEM_PROMPT_MAX_LENGTH:
            raise forms.ValidationError(
                f"AI 응답 방식은 {settings.SYSTEM_PROMPT_MAX_LENGTH:,}자 이하여야 합니다."
            )
        return value
