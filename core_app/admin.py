import csv
import json
from datetime import timedelta
from io import TextIOWrapper

from django.contrib import admin, messages
from django.core.management import call_command
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, FileResponse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .forms import ExportFileForm, ImportProxiesForm, ParsingLinkForm
from .models import (
    Advertisement,
    Brand,
    ExportCSV,
    ExportFile,
    Model,
    ParsingLink,
    ParsingTask,
    Part,
    PartGroup,
    Proxy,
    Translation,
    ApiToken,
    ExportedFile
)

from rangefilter.filters import DateRangeFilter


def export_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="export.csv"'
    writer = csv.writer(response)
    all_exports = ExportCSV.objects.all().order_by("number")
    if not all_exports:
        return
    writer.writerow([export_object.name for export_object in all_exports])

    for obj in queryset:
        writer.writerow(
            [getattr(obj, export_object.my_field) for export_object in all_exports]
        )
        obj.exported = True
        obj.save()
    return response


export_to_csv.short_description = "Export selected advertisements"


def copy_parsing_link_instance(modeladmin, request, queryset):
    instance = queryset.first()
    instance.name = "COPY " + instance.name
    instance.pk = None
    instance.save()

    new_instance = ParsingLink.objects.latest("pk")
    return redirect(f"/admin/core_app/parsinglink/{new_instance.pk}/change/")



@admin.register(ExportCSV)
class ExportCSVAdmin(admin.ModelAdmin):
    list_display = ("number", "name", "my_field")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "site_id")

    search_fields = (
        "name",
        "site_id",
    )


@admin.register(ParsingTask)
class ParsingTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "in_progress", "parsing_link")
    list_editable = ("order",)
    search_fields = ("id",)
    list_filter = ("in_progress",)
    ordering = ("-in_progress", "order")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("run-chain/", self.admin_site.admin_view(self.run_parsing_chain), name="run-chain"),
            path("refresh-chain/", self.admin_site.admin_view(self.refresh_parsing_chain), name="refresh-chain"),
            path("stop-chain/", self.admin_site.admin_view(self.stop_parsing_chain), name="stop-chain"),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context['custom_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def run_parsing_chain(self, request):
        call_command('run_chain')
        self.message_user(request, "Parsing chain started.")
        return HttpResponseRedirect("../")

    def refresh_parsing_chain(self, request):
        call_command("refresh_chain")
        self.message_user(request, "Refresh chain started.")
        return HttpResponseRedirect("../")

    def stop_parsing_chain(self, request):
        call_command("stop_chain")
        self.message_user(request, "Stop chain started.")
        return HttpResponseRedirect("../")


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "site_id")

    search_fields = (
        "name",
        "site_id",
    )
    list_filter = ("brand__name",)


@admin.register(PartGroup)
class PartGroupAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_ua", "site_id")

    search_fields = ("name_ru", "name_ua", "site_id")


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name_ru", "name_ua", "part_group", "site_id", "symbolic_code")

    search_fields = ("name_ru", "name_ua", "site_id", "symbolic_code")

    list_filter = ("part_group__name_ru",)


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ("polish_word", "translation_ru", "translation_ua")

    search_fields = ("polish_word", "translation_ru", "translation_ua")


@admin.register(ParsingLink)
class ParsingLinkAdmin(admin.ModelAdmin):
    form = ParsingLinkForm
    list_display = (
        "name",
        "part",
        "part_group",
        "brand",
        "model",
        "generation",
        "allegro_catalog_link",
        "active",
        "created_at",
        "update_at",
        "performed_at",
    )
    search_fields = (
        "model__name",
        "part__name_ru",
        "generation",
        "allegro_catalog_link",
    )
    list_filter = ("active", "brand__name", "model__name")
    readonly_fields = ("created_at", 'performed_at', 'update_at')
    actions = (copy_parsing_link_instance, )

    class Media:
        js = ('admin/js/admin/dynamic_dropdown.js', )


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "allegro_title",
        "part_name_ua",
        "is_active",
        "brand",
        "model",
        "created_at",
        "updated_at",
        "link",
        "generation",
        "price_euro",
        "exported",
    )

    search_fields = (
        "part_name_ua",
        "part_name_ru",
        "model",
        "price_euro",
        "generation",
        "allegro_id",
        "allegro_title",
    )
    list_filter = (
        "brand",
        "model",
        "part_name_ua",
        ("created_at", DateRangeFilter),
        "parsing_link",
        "exported",
        "is_active",
    )
    readonly_fields = ("symbolic_code_site",)

    def delete_all_advertisements(self, request, queryset):
        Advertisement.objects.all().delete()
        self.message_user(request, "Все объявления успешно удалены.", level=messages.SUCCESS)

    delete_all_advertisements.short_description = "Delete all"



    def link(self, obj):
        if obj.allegro_link:
            return format_html('<a href="{}" target="_blank">&#128279;</a>', obj.allegro_link)
        return "X"

    actions = [export_to_csv, delete_all_advertisements]


@admin.register(ExportFile)
class ExportFileAdmin(admin.ModelAdmin):
    form = ExportFileForm
    list_display = ("file_name", "schedule_time", "items_count", "created_at", "task")
    readonly_fields = ("created_at", "task")

    search_fields = (
        "file_name",
        "items_count",
        "created_at",
    )
    list_filter = (
        "schedule_time",
        "task",
    )

    @staticmethod
    def get_extra_context(extra_context):
        field_names = [field.name for field in Advertisement._meta.get_fields()]
        values_json = json.dumps(field_names, cls=DjangoJSONEncoder)

        extra_context = extra_context or {}
        extra_context["values"] = values_json

        return extra_context

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = self.get_extra_context(extra_context)

        return super().add_view(
            request, form_url, extra_context=extra_context
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = self.get_extra_context(extra_context)

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not obj.task:
            schedule_datetime = timezone.now().replace(
                hour=obj.schedule_time.hour,
                minute=obj.schedule_time.minute,
                second=0,
                microsecond=0,
            )

            if schedule_datetime < timezone.now():
                schedule_datetime += timedelta(days=1)

            schedule, created = CrontabSchedule.objects.get_or_create(
                minute=schedule_datetime.minute,
                hour=schedule_datetime.hour,
                day_of_month="*",  # Run every day
                month_of_year="*",  # Run every month
                day_of_week="*",  # Run every day of the week
            )

            task = PeriodicTask.objects.create(
                crontab=schedule,
                name=f"ExportFile_{obj.file_name}",
                task="core_app.tasks.export_advertisements_task",
                args=json.dumps([obj.id]),
            )
            obj.task = task
            obj.save()

    class Media:
        js = ("admin/js/custom_headers.js",)
        css = {"all": ("admin/css/custom_headers.css",)}


@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "port", "username", "password", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active", "port", "username", "password")
    search_fields = ("ip_address",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-proxies/",
                self.admin_site.admin_view(self.import_proxies),
                name="core_app_proxy_import_proxies",
            ),
        ]
        return custom_urls + urls

    def import_proxies(self, request):
        if request.method == "POST":
            form = ImportProxiesForm(request.POST, request.FILES)
            if form.is_valid():
                file = request.FILES["file"]
                if not file.name.endswith(".txt"):
                    self.message_user(
                        request, "Only .txt files are allowed", level=messages.ERROR
                    )
                else:
                    try:
                        proxies_added = 0
                        file_data = TextIOWrapper(file.file, encoding="utf-8")
                        reader = csv.reader(file_data)
                        for row in reader:
                            if len(row) != 4:
                                self.message_user(
                                    request,
                                    "Incorrect format in file",
                                    level=messages.ERROR,
                                )
                                return redirect("..")
                            ip_address, port, username, password = row
                            Proxy.objects.create(
                                ip_address=ip_address,
                                port=port,
                                username=username,
                                password=password,
                            )
                            proxies_added += 1
                        self.message_user(
                            request,
                            f"Successfully added {proxies_added} proxies",
                            level=messages.SUCCESS,
                        )
                    except Exception as e:
                        self.message_user(
                            request, f"Error processing file: {e}", level=messages.ERROR
                        )
                return redirect("..")
        else:
            form = ImportProxiesForm()

        return render(
            request, "admin/core_app/proxy/import_proxies.html", {"form": form}
        )

    def import_proxies_button(self, request):
        return format_html(
            '<a class="button" href="{}">Import Proxies</a>', "import-proxies"
        )

    import_proxies_button.short_description = "Import Proxies"
    import_proxies_button.allow_tags = True

    change_list_template = "admin/core_app/proxy/proxy_changelist.html"


@admin.register(ApiToken)
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = (
        "token",
        "email",
        "concurrent_requests"
    )


@admin.register(ExportedFile)
class ExportedFileAdmin(admin.ModelAdmin):
    list_display = (
        "filename",
        "created_at",
        'link'
    )

    def link(self, obj):
        from django.urls import reverse
        url = reverse('download_file', args=[obj.pk])
        return format_html(f'<a href="{url}">&#128279;</a>')
