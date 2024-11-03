from celery import shared_task

from .models import Advertisement, ExportFile, ParsingTask
from .utils import export_advertisements, parse_allegro_catalog
from asgiref.sync import async_to_sync


@shared_task
def export_advertisements_task(export_file_id):
    export_file = ExportFile.objects.get(id=export_file_id)
    advertisements = Advertisement.objects.filter(exported=False)
    export_advertisements(export_file, advertisements)


@shared_task
def do_parsing_task(parsing_task_order):
    print(f'Starting parsing task with order {parsing_task_order}')

    object = ParsingTask.objects.get(order=parsing_task_order)
    object.in_progress = True
    object.save()
    parse_allegro_catalog(object.parsing_link)
    object.in_progress = False
    object.save()
