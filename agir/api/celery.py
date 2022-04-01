import logging
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agir.api.settings")

app = Celery("agir.api")

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


logger = logging.getLogger("agir.api.celery")


_memory_tracker = None


def get_memory_tracker():
    global _memory_tracker
    if _memory_tracker is None:
        from pympler.tracker import SummaryTracker

        _memory_tracker = SummaryTracker()
    return _memory_tracker


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))


@app.task
def memory_summary():
    from pympler import muppy, summary

    all_objects = muppy.get_objects()
    obj_summary = summary.summarize(all_objects)

    logger.info("\n".join(summary.format_(obj_summary)))


@app.task
def memory_tracker():
    logger.info("\n".join(get_memory_tracker().format_diff()))
