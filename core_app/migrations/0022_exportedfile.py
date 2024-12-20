# Generated by Django 5.0.6 on 2024-08-02 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core_app", "0021_alter_advertisement_created_at"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportedFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("filename", models.CharField(max_length=255)),
                ("file", models.FileField(upload_to="exports")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
