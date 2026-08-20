import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "priority_poke.settings")
application = get_wsgi_application()

from tracker.scheduler import start_notification_scheduler

start_notification_scheduler()
