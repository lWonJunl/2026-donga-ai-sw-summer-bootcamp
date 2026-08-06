from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tracker", "0006_classgroup_show_member_progress_peerreminder"),
    ]

    operations = [
        migrations.RenameField(
            model_name="classgroup",
            old_name="course_name",
            new_name="name",
        ),
        migrations.AlterField(
            model_name="classgroup",
            name="name",
            field=models.CharField(max_length=100, verbose_name="그룹 이름"),
        ),
        migrations.AddField(
            model_name="classgroup",
            name="description",
            field=models.TextField(blank=True, verbose_name="그룹 설명"),
        ),
        migrations.RemoveField(model_name="classgroup", name="academic_year"),
        migrations.RemoveField(model_name="classgroup", name="semester"),
        migrations.RemoveField(model_name="classgroup", name="section"),
        migrations.RemoveField(model_name="classgroup", name="professor"),
        migrations.RemoveField(model_name="classgroup", name="nickname"),
        migrations.AlterModelOptions(
            name="classgroup",
            options={"ordering": ["name", "-created_at"]},
        ),
    ]
