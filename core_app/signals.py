import os

from django.db.models import Max
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from core_app.models import ParsingTask, ParsingLink, ExportedFile, ExportFile

changing = False


@receiver(pre_save, sender=ParsingTask)
def update_parsing_task(sender, instance, **kwargs):
    global changing

    if not changing:
        try:
            task_before = ParsingTask.objects.get(id=instance.id)
            existing_task = ParsingTask.objects.get(order=instance.order)
            existing_task.order = task_before.order
            changing = True
            existing_task.save()
        except ParsingTask.DoesNotExist:
            pass
    elif changing:
        changing = False


@receiver(post_save, sender=ParsingLink)
def create_parsing_task(sender, instance, created, **kwargs):
    if created:
        max_order = ParsingTask.objects.aggregate(Max('order')).get('order__max') or 0
        new_order = max_order + 1
        ParsingTask.objects.create(order=new_order, in_progress=False, parsing_link=instance)


@receiver(post_delete, sender=ExportedFile)
def delete_exported_file(sender, instance, **kwargs):
    if os.path.exists(instance.filepath):
        os.remove(instance.filepath)