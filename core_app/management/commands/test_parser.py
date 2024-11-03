from django.core.management.base import BaseCommand

from core_app.models import ParsingTask
from core_app.tasks import do_parsing_task


class Command(BaseCommand):
    help = "Just a command for launching a parsing chain."

    def handle(self, *args, **kwargs):

        for x in ParsingTask.objects.filter(order__gt=0).order_by("order"):
            do_parsing_task(x.order)
