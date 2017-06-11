from django.core.management.base import BaseCommand
import os
import binascii

from django.contrib.auth.models import Group

from ...models import Client


def generate_secret():
    return binascii.hexlify(os.urandom(30)).decode('ascii')


class Command(BaseCommand):
    help = "Creates or update client"

    def add_arguments(self, parser):
        parser.add_argument('clientlabel')
        parser.add_argument(
            '--group',
            metavar='GROUP',
            dest='groups',
            action='append'
        )
        parser.add_argument(
            '--gen-passwd',
            dest='generate_password',
            action='store_true'
        )

    def handle(self, *args, clientlabel, generate_password, groups, **options):
        if generate_password:
            secret = generate_secret()
        else:
            secret = os.environ.get('CLIENT_SECRET')

        client, created = Client.objects.get_or_create(label=clientlabel)

        if secret:
            client.role.set_password(secret)
            client.role.save()

        current_groups = [group.name for group in client.role.groups.all()]

        for group in (groups or []):
            if group not in current_groups:
                client.role.groups.add(Group.objects.get(name=group))

        return secret or ''
