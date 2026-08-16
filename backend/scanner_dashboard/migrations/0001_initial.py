from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ScanResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("category", models.CharField(choices=[("cloud", "클라우드 인프라"), ("code", "코드"), ("phishing", "피싱")], max_length=20)),
                ("target", models.CharField(max_length=500)),
                ("is_risky", models.BooleanField()),
                ("detail", models.TextField(blank=True)),
                ("ai_explanation", models.TextField(blank=True)),
                ("scanned_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-scanned_at"],
            },
        ),
    ]
