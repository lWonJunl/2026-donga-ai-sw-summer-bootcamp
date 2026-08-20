import django.db.models.deletion
import tracker.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="ClassGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("academic_year", models.PositiveSmallIntegerField(verbose_name="학년도")),
                ("semester", models.CharField(choices=[("first", "1학기"), ("second", "2학기"), ("summer", "여름학기"), ("winter", "겨울학기")], max_length=10, verbose_name="학기")),
                ("course_name", models.CharField(max_length=100, verbose_name="과목명")),
                ("section", models.CharField(max_length=30, verbose_name="분반")),
                ("professor", models.CharField(blank=True, max_length=50, verbose_name="담당 교수")),
                ("nickname", models.CharField(blank=True, max_length=50, verbose_name="그룹 별칭")),
                ("invite_code", models.CharField(default=tracker.models.create_invite_code, editable=False, max_length=8, unique=True, verbose_name="초대 코드")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_class_groups", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-academic_year", "semester", "course_name", "section"]},
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150, verbose_name="과제명")),
                ("description", models.TextField(blank=True, verbose_name="설명")),
                ("due_at", models.DateTimeField(verbose_name="제출 마감")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_assignments", to=settings.AUTH_USER_MODEL)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="tracker.classgroup")),
            ],
            options={"ordering": ["due_at"]},
        ),
        migrations.CreateModel(
            name="AssignmentProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("todo", "시작 전"), ("doing", "진행 중"), ("done", "완료")], default="todo", max_length=10)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("assignment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_records", to="tracker.assignment")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assignment_progress", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="GroupMembership",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("owner", "관리자"), ("member", "구성원")], default="member", max_length=10)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("group", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="tracker.classgroup")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="class_memberships", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name="assignment",
            constraint=models.UniqueConstraint(fields=("group", "title", "due_at"), name="unique_assignment_in_group"),
        ),
        migrations.AddConstraint(
            model_name="assignmentprogress",
            constraint=models.UniqueConstraint(fields=("assignment", "user"), name="unique_assignment_progress"),
        ),
        migrations.AddConstraint(
            model_name="groupmembership",
            constraint=models.UniqueConstraint(fields=("group", "user"), name="unique_group_member"),
        ),
    ]
