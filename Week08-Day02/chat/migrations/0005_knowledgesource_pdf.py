from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("chat", "0004_knowledgesource_message_sources")]

    operations = [
        migrations.AlterField(
            model_name="knowledgesource",
            name="source_type",
            field=models.CharField(
                choices=[("url", "URL"), ("pptx", "PPTX"), ("docx", "DOCX"), ("pdf", "PDF")],
                max_length=10,
            ),
        ),
    ]
