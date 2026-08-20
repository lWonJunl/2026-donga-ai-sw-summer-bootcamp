from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0005_assignmentnotification"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="classgroup",
            name="show_member_progress",
            field=models.BooleanField(
                default=False,
                help_text="그룹 구성원이 서로의 과제 진행 상태를 확인하고 미완료 구성원을 찌를 수 있습니다.",
                verbose_name="구성원 진행 상태 공개",
            ),
        ),
        migrations.CreateModel(
            name="PeerReminder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("delivered_count", models.PositiveSmallIntegerField(default=0)),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="peer_reminders", to="tracker.assignment")),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_peer_reminders", to=settings.AUTH_USER_MODEL)),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sent_peer_reminders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-sent_at"]},
        ),
    ]
