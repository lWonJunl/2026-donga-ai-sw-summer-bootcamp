from django.conf import settings
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserPreference


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        clean_one = super().clean
        if isinstance(data, (list, tuple)):
            return [clean_one(item, initial) for item in data]
        return [clean_one(data, initial)] if data else []


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


class KnowledgeIngestForm(forms.Form):
    urls = forms.CharField(
        required=False,
        label="수집할 URL",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "URL을 한 줄에 하나씩 입력하세요."}),
    )
    files = MultipleFileField(required=False, label="PDF·PPTX·DOCX 파일")

    def clean_urls(self):
        urls = [line.strip() for line in self.cleaned_data["urls"].splitlines() if line.strip()]
        if len(urls) > 10:
            raise forms.ValidationError("URL은 한 번에 10개까지 수집할 수 있습니다.")
        return urls

    def clean_files(self):
        files = self.cleaned_data.get("files", [])
        if len(files) > 10:
            raise forms.ValidationError("파일은 한 번에 10개까지 업로드할 수 있습니다.")
        return files

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("urls") and not cleaned.get("files"):
            raise forms.ValidationError("URL 또는 파일을 하나 이상 제출하세요.")
        return cleaned
