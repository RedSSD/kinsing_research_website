from threading import Thread

from celery import current_app
from celery.result import AsyncResult
from django.core.management.base import BaseCommand

from core_app.models import TaskChain


class Command(BaseCommand):
    help = "Just a command for refreshing a parsing chain."

    def handle(self, *args, **kwargs):
        Thread(target=self.refresh_chain).start()

    def refresh_chain(self):
        print("Refresh task chain...")

        task_chain_object = TaskChain.objects.last()
        last_task = 0

        if task_chain_object:

            for order in task_chain_object.chain_ids.keys():

                async_result = AsyncResult(task_chain_object.chain_ids[order], app=current_app)

                if not last_task and async_result.state in ["PENDING", "STARTED"]:
                    last_task = order
                async_result.revoke(terminate=True, signal="SIGKILL")

            task_chain_object.start_from = last_task
            task_chain_object.save()
