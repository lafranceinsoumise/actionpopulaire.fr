import shutil
import tempfile
from django.test import override_settings
from django.test.runner import DiscoverRunner

from .celery import app


class TempMediaMixin(object):
    "Mixin to create MEDIA_ROOT in temp and tear down when complete."

    def setup_test_environment(self):
        "Create temp directory and update MEDIA_ROOT and default storage."
        super(TempMediaMixin, self).setup_test_environment()

        self._temp_media = tempfile.mkdtemp()
        self.media_settings_overrider = override_settings(
            MEDIA_ROOT=self._temp_media,
            DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
        )
        self.media_settings_overrider.enable()

    def teardown_test_environment(self):
        "Delete temp storage."
        super(TempMediaMixin, self).teardown_test_environment()
        shutil.rmtree(self._temp_media, ignore_errors=True)
        self.media_settings_overrider.disable()


class TestRunner(TempMediaMixin, DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super().setup_test_environment(**kwargs)
        app.conf.task_always_eager = True
