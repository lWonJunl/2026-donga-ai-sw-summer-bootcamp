from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UserPreference(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preference"
    )
    system_prompt = models.TextField(
        default="당신은 초보자를 돕는 친절한 AI 강사입니다. 한국어로 쉽게 설명하고 필요하면 예제를 보여주세요."
    )
    temperature = models.FloatField(
        default=0.7, validators=[MinValueValidator(0.0), MaxValueValidator(1.5)]
    )

    def __str__(self):
        return f"{self.user.username}의 설정"


class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations"
    )
    title = models.CharField(max_length=80, default="새 대화")
    title_is_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Message(models.Model):
    ROLE_CHOICES = [("user", "사용자"), ("assistant", "AI")]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.role}"
