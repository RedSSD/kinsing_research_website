from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alegro_parser.settings')

app = Celery('alegro_parser', broker='redis://redis:6379/0')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.task_queues = {
    'parsing_queue': {
        'exchange': 'parsing_exchange',
        'exchange_type': 'direct',
        'routing_key': 'parsing_key',
    },
    'export_queue': {
        'exchange': 'export_exchange',
        'exchange_type': 'direct',
        'routing_key': 'export_key',
    },
}
app.conf.task_routes = {
    'core_app.tasks.do_parsing_task': {'queue': 'parsing_queue'},
    'core_app.tasks.export_advertisements_task': {'queue': 'export_queue'},
}

app.autodiscover_tasks()
