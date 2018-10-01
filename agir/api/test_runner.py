from django.test.runner import DiscoverRunner
from .celery import app


class TestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        app.conf.task_always_eager = True
