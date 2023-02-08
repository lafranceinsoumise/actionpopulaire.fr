from django.core import management
from django.utils import translation
from tqdm import tqdm


class BaseCommand(management.BaseCommand):
    language = "en"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.tqdm = None
        self.dry_run = None
        self.silent = False

    def execute(self, *args, dry_run=False, silent=False, **options):
        self.dry_run = dry_run
        self.silent = silent
        default_language = translation.get_language()
        translation.activate(self.language)
        self.log("\n")
        output = super().execute(*args, **options)
        translation.activate(default_language)
        self.log("\n👋 Bye!\n\n")
        return output

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Execute without creating any event request",
        )
        parser.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action="store_true",
            default=False,
            help="Display a progress bar during the script execution",
        )

    def log(self, message):
        if self.silent:
            return
        if self.tqdm:
            self.tqdm.clear()
        if not isinstance(message, str):
            message = str(message)
        self.stdout.write(message)

    def info(self, message):
        self.log(self.style.MIGRATE_HEADING(f"{message}"))

    def warning(self, message):
        self.log(self.style.WARNING(f"⚠ {message}"))

    def success(self, message):
        if self.dry_run:
            message = "[DRY-RUN] " + message
        self.log(self.style.SUCCESS(f"✔ {message}"))

    def error(self, message):
        if self.dry_run:
            message = "[DRY-RUN] " + message
        self.log(self.style.ERROR(f"✖ {message}"))

    def log_current_item(self, item):
        self.tqdm.set_description_str(str(item))

    def init_tqdm(self, total, **kwargs):
        self.tqdm = tqdm(
            total=total,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            disable=self.silent or total == 1,
            colour="#cbbfec",
            **kwargs,
        )

    def handle(self, *args, **options):
        self.log("Nothing to do!")
        return
