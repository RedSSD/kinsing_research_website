from threading import Thread

from celery import chain
from celery.exceptions import TaskRevokedError
from django.core.management.base import BaseCommand

from core_app.models import ParsingTask, TaskChain
from core_app.tasks import do_parsing_task


class Command(BaseCommand):
    help = "Just a command for launching a parsing chain."

    def handle(self, *args, **kwargs):
        Thread(target=self.task_chain).start()

    def task_chain(self):
        chain_start = 0

        while True:

            print("Start parsing chain...")

            chain_tasks = []
            ordering = []
            for x in ParsingTask.objects.filter(order__gt=int(chain_start)).order_by("order"):
                ordering.append(x.order)
                chain_tasks.append(do_parsing_task.si(x.order))

            task_chain = chain(*chain_tasks)
            result = task_chain.apply_async()

            chain_ids = {ordering[counter]: result.as_list()[-(counter + 1)] for counter in range(len(ordering))}

            TaskChain.objects.all().delete()
            db_object = TaskChain.objects.create(chain_ids=chain_ids)
            try:
                result.get()
                TaskChain.objects.get(id=db_object.pk).delete()
                chain_start = 0
            except TaskRevokedError:
                task_chain_last = TaskChain.objects.last()
                if task_chain_last:
                    print("Chain was refreshed")
                    chain_start = task_chain_last.start_from
                elif not task_chain_last:
                    print("Chain was stopped")
                    return
            except TaskChain.DoesNotExist:
                print("Chain was stopped")
                return
