# Generated by Django 5.0.6 on 2024-06-13 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_app', '0012_alter_advertisement_allegro_price_pln'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advertisement',
            name='generation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='label_1',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='label_2',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='advertisement',
            name='label_3',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]