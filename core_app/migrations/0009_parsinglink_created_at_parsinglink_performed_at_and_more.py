# Generated by Django 5.0.6 on 2024-06-12 09:25

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0008_parsingtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='parsinglink',
            name='created_at',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='parsinglink',
            name='performed_at',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parsinglink',
            name='update_at',
            field=models.DateField(auto_now=True),
        ),
    ]
