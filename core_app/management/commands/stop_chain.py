from threading import Thread

from celery import current_app
from celery.result import AsyncResult
from django.core.management.base import BaseCommand

from core_app.models import TaskChain, ParsingTask


class Command(BaseCommand):
    help = "Just a command for stopping a parsing chain."

    def handle(self, *args, **kwargs):
        Thread(target=self.stop_chain).start()

    def stop_chain(self):
        print("Stop task chain...")

        task_chain_object = TaskChain.objects.last()

        if task_chain_object:

            for order in task_chain_object.chain_ids.keys():

                async_result = AsyncResult(task_chain_object.chain_ids[order], app=current_app)
                async_result.revoke(terminate=True, signal="SIGKILL")

            task_chain_object.delete()

        tasks = ParsingTask.objects.all()
        for task in tasks:
            task.in_progress = False
            task.save()
