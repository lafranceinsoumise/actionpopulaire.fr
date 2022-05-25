import os
import shutil
import tempfile

from django.test import override_settings
from django.test.runner import DiscoverRunner
from hypothesis import settings, Verbosity, HealthCheck

from .celery import app
from .redis import using_separate_redis_server


class TestRunner(DiscoverRunner):
    "Mixin to create MEDIA_ROOT in temp and tear down when complete."

    def setup_test_environment(self):
        """Met en place un environnement de test adapté.

        Réalise les actions suivantes :
        - Crée un dossier temporaire pour les fichiers média et modifie le paramètre MEDIA_ROOT
        - Met en place un serveur Redis standalone pour les tests
        - Met Celery en mode "eager", c'est-à-dire que les tâches sont exécutées immédiatement
          plutôt que d'être schedulées
        - Select hypothesis profile from env var
        :return:
        """
        super(TestRunner, self).setup_test_environment()

        self._temp_media = tempfile.mkdtemp()
        self.settings_overrider = override_settings(
            MEDIA_ROOT=self._temp_media,
            DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
            STATICFILES_STORAGE=(
                "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        )
        self.settings_overrider.enable()

        self._redislite = using_separate_redis_server()
        self._redislite.__enter__()

        app.conf.task_always_eager = True

        settings.register_profile(
            "ci", max_examples=10, suppress_health_check=[HealthCheck.too_slow]
        )
        settings.register_profile("dev", deadline=1000)
        settings.register_profile("debug", deadline=1000, verbosity=Verbosity.verbose)
        settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "ci"))

    def teardown_test_environment(self):
        "On défait tout ce qui a été fait au setup dans l'ordre inverse"
        app.conf.task_always_eager = False

        self._redislite.__exit__(None, None, None)

        self.settings_overrider.disable()
        shutil.rmtree(self._temp_media, ignore_errors=True)

        super(TestRunner, self).teardown_test_environment()
