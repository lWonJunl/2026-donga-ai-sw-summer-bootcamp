import logging
import threading
import time

from django.conf import settings
from django.db import close_old_connections

from .notifications import send_assignment_notifications


logger = logging.getLogger(__name__)
_start_lock = threading.Lock()
_started = False


def _notification_loop():
    interval = settings.NOTIFICATION_SCHEDULER_INTERVAL_SECONDS
    while True:
        started_at = time.monotonic()
        close_old_connections()
        try:
            summary = send_assignment_notifications()
            logger.info("Automatic push notification run completed: %s", summary)
        except Exception:
            logger.exception("Automatic push notification run failed")
        finally:
            close_old_connections()

        elapsed = time.monotonic() - started_at
        time.sleep(max(1, interval - elapsed))


def start_notification_scheduler():
    """Start one scheduler thread in the current WSGI worker process."""
    global _started

    if not settings.RUN_NOTIFICATION_SCHEDULER:
        return
    if not settings.WEBPUSH_VAPID_PRIVATE_KEY or not settings.WEBPUSH_VAPID_PUBLIC_KEY:
        logger.warning("Automatic push scheduler is disabled because VAPID keys are missing")
        return

    with _start_lock:
        if _started:
            return
        _started = True
        thread = threading.Thread(
            target=_notification_loop,
            name="priority-poke-notification-scheduler",
            daemon=True,
        )
        thread.start()
        logger.info(
            "Automatic push scheduler started with a %s-second interval",
            settings.NOTIFICATION_SCHEDULER_INTERVAL_SECONDS,
        )
