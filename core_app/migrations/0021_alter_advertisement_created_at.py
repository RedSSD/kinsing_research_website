# Generated by Django 5.0.6 on 2024-08-02 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core_app", "0020_alter_apitoken_concurrent_requests"),
    ]

    operations = [
        migrations.AlterField(
            model_name="advertisement",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
