from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helsinkiCityBikeApp.settings')
app = Celery('helsinkiCityBikeApp')
app.conf.enable_utc = False
app.conf.update(timezone = "Europe/Helsinki")
app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))