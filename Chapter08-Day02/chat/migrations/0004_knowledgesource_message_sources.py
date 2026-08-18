from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0003_conversation_title_is_custom"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="sources",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.CreateModel(
            name="KnowledgeSource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_type", models.CharField(choices=[("url", "URL"), ("pptx", "PPTX"), ("docx", "DOCX")], max_length=10)),
                ("source", models.TextField()),
                ("display_name", models.CharField(max_length=255)),
                ("content_hash", models.CharField(blank=True, max_length=64)),
                ("chunk_count", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(choices=[("processing", "처리 중"), ("ready", "완료"), ("failed", "실패")], default="processing", max_length=20)),
                ("error", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="knowledge_sources", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
