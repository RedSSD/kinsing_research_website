import re
import string
from random import choices
from traceback import print_exc

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_celery_beat.models import PeriodicTask

from alegro_parser.settings import EXPOERTED_FILE_BASE_PATH


def generate_article():
    date_str = timezone.now().strftime("%d%m%y")
    random_str = "".join(choices(string.ascii_uppercase + string.digits, k=10))
    return f"A{date_str}{random_str}"


class Brand(models.Model):
    name = models.CharField(max_length=255)
    site_id = models.IntegerField()

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, related_name="models", on_delete=models.CASCADE)
    site_id = models.IntegerField()

    def __str__(self):
        return self.name


class PartGroup(models.Model):
    name_ru = models.CharField(max_length=255)
    name_ua = models.CharField(max_length=255)
    site_id = models.IntegerField()

    def __str__(self):
        return self.name_ru


class Part(models.Model):
    name_ru = models.CharField(max_length=255)
    name_ua = models.CharField(max_length=255)
    part_group = models.ForeignKey(
        PartGroup, related_name="parts", on_delete=models.CASCADE
    )
    site_id = models.IntegerField()
    symbolic_code = models.CharField(max_length=255)

    def __str__(self):
        return self.name_ru


class Translation(models.Model):
    polish_word = models.CharField(max_length=255, help_text="Example: korozji or korozji/korozja/rdza")
    translation_ru = models.CharField(max_length=255)
    translation_ua = models.CharField(max_length=255)

    def __str__(self):
        return self.polish_word


class ParsingLink(models.Model):
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    part_group = models.ForeignKey(PartGroup, on_delete=models.CASCADE)
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    generation = models.CharField(max_length=255, null=True, blank=True)
    allegro_catalog_link = models.URLField()
    price_formula = models.CharField(max_length=255)
    description_ua = models.TextField()
    description_ru = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    update_at = models.DateField(auto_now=True)
    performed_at = models.DateField(null=True, blank=True)
    label_1 = models.CharField(max_length=255, null=True, blank=True)
    label_2 = models.CharField(max_length=255, null=True, blank=True)
    label_3 = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.brand.name} {self.model.name} {self.part.name_ru}"


class ParsingTask(models.Model):
    order = models.BigIntegerField()
    in_progress = models.BooleanField()
    parsing_link = models.ForeignKey(ParsingLink, on_delete=models.CASCADE)


def auto_replace_description(description, title, vin, article, generation, language):
    # Replace placeholders for vin, article, and generation
    description = description.replace("{{vin}}", vin if vin and vin != "N/A" else "")
    description = description.replace("{{article}}", article or "")
    description = description.replace("{{generation}}", generation or "")

    translations = Translation.objects.all()
    translation_string = ""
    if translations:
        for translation in translations:
            for word in translation.polish_word.split("/"):
                if word.lower() in title.lower():
                    translation_string += translation.translation_ua if language == "ua" else translation.translation_ru
                    translation_string += " "
                    break

    description = description.replace("{{translate}}", translation_string or "")

    return description


class Advertisement(models.Model):
    part_name_ua = models.CharField(max_length=255)
    part_name_ru = models.CharField(max_length=255)
    part_group_name_ua = models.CharField(max_length=255)
    part_group_name_ru = models.CharField(max_length=255)
    part_site_id = models.IntegerField()
    part_group_site_id = models.IntegerField()
    symbolic_code = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    brand_site_id = models.IntegerField()
    model = models.CharField(max_length=255)
    model_site_id = models.IntegerField()
    generation = models.CharField(max_length=255, null=True, blank=True)
    description_ua = models.TextField()
    description_ru = models.TextField()
    label_1 = models.CharField(max_length=255, null=True, blank=True)
    label_2 = models.CharField(max_length=255, null=True, blank=True)
    label_3 = models.CharField(max_length=255, null=True, blank=True)
    price_euro = models.CharField(max_length=255)
    symbolic_code_site = models.CharField(max_length=255, editable=False)
    article = models.CharField(max_length=255, default=generate_article, unique=True)
    allegro_link = models.URLField()
    allegro_id = models.CharField(max_length=255)
    allegro_price_pln = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    allegro_title = models.CharField(max_length=255)
    vin = models.CharField(max_length=255, blank=True, null=True)
    allegro_seller = models.CharField(max_length=255)
    allegro_images = models.TextField()  # Images stored as a semicolon-separated list
    parsing_link = models.ForeignKey(ParsingLink, on_delete=models.CASCADE)
    exported = models.BooleanField(default=False)  # Flag to indicate if exported
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        try:
            if self.allegro_price_pln is not None:
                formula = self.price_euro.replace(
                    "{{allegro_price}}", str(self.allegro_price_pln)
                )
                self.price_euro = eval(formula, {"__builtins__": None}, {})
            else:
                raise ValidationError(
                    "allegro_price_pln must be set for price calculation."
                )

            self.symbolic_code_site = f"{self.symbolic_code}-{self.article}"

            # Apply substitutions and translations
            self.description_ua = auto_replace_description(
                self.description_ua, self.allegro_title, self.vin, self.article, self.generation, "ua"
            )
            self.description_ru = auto_replace_description(
                self.description_ru, self.allegro_title, self.vin, self.article, self.generation, "ru"
            )

            super().save(*args, **kwargs)
        except Exception as e:
            print_exc()

    def __str__(self):
        return self.part_name_ua


class ExportFile(models.Model):
    file_name = models.CharField(max_length=255)
    schedule_time = models.TimeField()
    items_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.OneToOneField(
        PeriodicTask, on_delete=models.SET_NULL, null=True, blank=True
    )
    custom_headers = models.JSONField(
        default=dict, blank=True
    )  # Custom headers for the fields

    def __str__(self):
        return self.file_name


class Proxy(models.Model):
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.username and self.password:
            return f"{self.ip_address}:{self.port} ({self.username}:{self.password})"
        else:
            return f"{self.ip_address}:{self.port}"


class ExportCSV(models.Model):
    MY_CHOICES = [
        ("part_name_ua", "part_name_ua"),
        ("part_name_ru", "part_name_ru"),
        ("part_group_name_ua", "part_group_name_ua"),
        ("part_group_name_ru", "part_group_name_ru"),
        ("part_site_id", "part_site_id"),
        ("part_group_site_id", "part_group_site_id"),
        ("symbolic_code", "symbolic_code"),
        ("brand", "brand"),
        ("brand_site_id", "brand_site_id"),
        ("model", "model"),
        ("model_site_id", "model_site_id"),
        ("generation", "generation"),
        ("description_ua", "description_ua"),
        ("description_ru", "description_ru"),
        ("label_1", "label_1"),
        ("label_2", "label_2"),
        ("label_3", "label_3"),
        ("price_euro", "price_euro"),
        ("symbolic_code_site", "symbolic_code_site"),
        ("article", "article"),
        ("allegro_link", "allegro_link"),
        ("allegro_id", "allegro_id"),
        ("allegro_price_pln", "allegro_price_pln"),
        ("allegro_title", "allegro_title"),
        ("vin", "vin"),
        ("allegro_seller", "allegro_seller"),
        ("allegro_images", "allegro_images"),
        ("parsing_link", "parsing_link"),
        ("exported", "exported"),
    ]

    number = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    my_field = models.CharField(max_length=255, choices=MY_CHOICES)


class TaskChain(models.Model):
    chain_ids = models.JSONField()
    start_from = models.IntegerField(default=0)


class ApiToken(models.Model):
    token = models.CharField(max_length=255, help_text="Service token")
    email = models.EmailField(blank=True, help_text="Email address of the account")
    concurrent_requests = models.PositiveIntegerField(blank=False, default=1, help_text="Number of concurrent requests")


class ExportedFile(models.Model):
    filename = models.CharField(max_length=255)
    filepath = models.FilePathField(path="/code/exports")
    created_at = models.DateTimeField(auto_now_add=True)
