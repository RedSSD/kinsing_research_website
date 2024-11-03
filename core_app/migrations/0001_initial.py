# Generated by Django 5.0.6 on 2024-05-20 14:12

import core_app.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_beat', '0018_improve_crontab_helptext'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('site_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Part',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ru', models.CharField(max_length=255)),
                ('name_ua', models.CharField(max_length=255)),
                ('site_id', models.IntegerField()),
                ('symbolic_code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PartGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_ru', models.CharField(max_length=255)),
                ('name_ua', models.CharField(max_length=255)),
                ('site_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('polish_word', models.CharField(max_length=255)),
                ('translation_ru', models.CharField(max_length=255)),
                ('translation_ua', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('site_id', models.IntegerField()),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='core_app.brand')),
            ],
        ),
        migrations.CreateModel(
            name='ParsingLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True)),
                ('generation', models.CharField(max_length=255)),
                ('allegro_catalog_link', models.URLField()),
                ('price_formula', models.CharField(max_length=255)),
                ('description_ua', models.TextField()),
                ('description_ru', models.TextField()),
                ('label_1', models.CharField(max_length=255)),
                ('label_2', models.CharField(max_length=255)),
                ('label_3', models.CharField(max_length=255)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.brand')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.model')),
                ('part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.part')),
                ('part_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.partgroup')),
            ],
        ),
        migrations.CreateModel(
            name='ExportFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('schedule_time', models.DateTimeField()),
                ('items_count', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.periodictask')),
                ('parsing_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.parsinglink')),
            ],
        ),
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_name_ua', models.CharField(max_length=255)),
                ('part_name_ru', models.CharField(max_length=255)),
                ('part_group_name_ua', models.CharField(max_length=255)),
                ('part_group_name_ru', models.CharField(max_length=255)),
                ('part_site_id', models.IntegerField()),
                ('part_group_site_id', models.IntegerField()),
                ('symbolic_code', models.CharField(max_length=255)),
                ('brand_site_id', models.IntegerField()),
                ('model_site_id', models.IntegerField()),
                ('generation', models.CharField(max_length=255)),
                ('description_ua', models.TextField()),
                ('description_ru', models.TextField()),
                ('label_1', models.CharField(max_length=255)),
                ('label_2', models.CharField(max_length=255)),
                ('label_3', models.CharField(max_length=255)),
                ('price_euro', models.DecimalField(decimal_places=2, max_digits=10)),
                ('symbolic_code_site', models.CharField(editable=False, max_length=255)),
                ('article', models.CharField(default=core_app.models.generate_article, max_length=255, unique=True)),
                ('allegro_link', models.URLField()),
                ('allegro_id', models.CharField(max_length=255)),
                ('allegro_price_pln', models.DecimalField(decimal_places=2, max_digits=10)),
                ('allegro_title', models.CharField(max_length=255)),
                ('vin', models.CharField(blank=True, max_length=255, null=True)),
                ('allegro_seller', models.CharField(max_length=255)),
                ('allegro_images', models.TextField()),
                ('exported', models.BooleanField(default=False)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.brand')),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.model')),
                ('parsing_link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core_app.parsinglink')),
            ],
        ),
        migrations.AddField(
            model_name='part',
            name='part_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parts', to='core_app.partgroup'),
        ),
    ]