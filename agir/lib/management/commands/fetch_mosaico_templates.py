import re
from pathlib import Path
import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Fetch all mosaico mails'

    def handle(self, *args, **options):
        # create target directory in case it does not exist
        target = Path('./agir/lib/templates/mail_templates/')
        target.mkdir(0o755, True, True)

        var_regex = re.compile(r'\[([-A-Z_]+)\]')
        var_files = re.compile(r'^([-A-Za-z_]+)\.html$')

        for file in target.glob('*.html'):
            match = var_files.match(file.name)
            if match and match.group(1) not in settings.EMAIL_TEMPLATES:
                file.unlink()

        for name, url in settings.EMAIL_TEMPLATES.items():
            try:
                res = requests.get(url)
                res.raise_for_status()
            except requests.RequestException:
                raise CommandError('Could not fetch url "{}"'.format(url))

            content = var_regex.sub(r'{{ \1 }}', res.text)

            with target.joinpath(name + '.html').open('w') as f:
                f.write(content)
