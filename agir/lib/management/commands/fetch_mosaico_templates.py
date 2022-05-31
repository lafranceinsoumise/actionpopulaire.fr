from pathlib import Path

import re
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from agir.lib.mailing import generate_plain_text, fetch_mosaico_template

LIB_APP_DIR = Path(__file__).parent.parent.parent


class Command(BaseCommand):
    help = "Fetch all mosaico mails"

    def handle(self, *args, **options):
        # create target directory in case it does not exist
        target_dir = LIB_APP_DIR / "templates" / "mail_templates"
        target_dir.mkdir(0o755, parents=True, exist_ok=True)

        var_files = re.compile(r"^([-A-Za-z_]+)\.(?:html|txt)$")

        for file in target_dir.iterdir():
            match = var_files.match(file.name)
            if match and match.group(1) not in settings.EMAIL_TEMPLATES:
                # delete all
                file.unlink()

        for name, url in tqdm(settings.EMAIL_TEMPLATES.items()):
            if not url:
                continue
            try:
                content = fetch_mosaico_template(url)
            except requests.RequestException:
                raise CommandError('Could not fetch url "{}"'.format(url))

            html_file = target_dir.joinpath(f"{name}.html")
            txt_file = target_dir.joinpath(f"{name}.txt")

            previous_content = None
            if html_file.exists():
                with html_file.open("r") as f:
                    previous_content = f.read()

            with html_file.open("w") as f:
                f.write(content)

            if not txt_file.exists() or content != previous_content:
                txt_content = generate_plain_text(content)

                with txt_file.open("w") as f:
                    f.write(txt_content)
