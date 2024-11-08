# Generated by Django 5.0.6 on 2024-08-02 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core_app", "0017_apitoken"),
    ]

    operations = [
        migrations.AlterField(
            model_name="apitoken",
            name="email",
            field=models.EmailField(
                blank=True, help_text="Email address of the account", max_length=254
            ),
        ),
        migrations.AlterField(
            model_name="apitoken",
            name="token",
            field=models.CharField(help_text="Service token", max_length=255),
        ),
    ]
