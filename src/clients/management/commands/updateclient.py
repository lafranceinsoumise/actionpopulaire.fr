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
        parser.add_argument(
            '--oauth',
            dest='oauth',
            action='store_true'
        )

    def handle(self, *args, clientlabel, generate_password, groups, oauth, **options):
        if generate_password:
            secret = generate_secret()
        else:
            secret = os.environ.get('CLIENT_SECRET')

        client, created = Client.objects.get_or_create(label=clientlabel)

        if created:
            self.stdout.write(self.style.SUCCESS('Created client'))

        if secret and not client.role.check_password(secret):
            client.role.set_password(secret)
            client.role.save()
            self.stdout.write('Set secret to new value')

        if client.oauth_enabled != oauth:
            client.oauth_enabled = oauth
            client.save()
            self.stdout.write('Enabled oauth for client' if oauth else 'Disabled oauth for client')

        current_groups = [group.name for group in client.role.groups.all()]

        for group in (groups or []):
            if group not in current_groups:
                client.role.groups.add(Group.objects.get(name=group))
                self.stdout.write('Added client to group %s' % group)

        for group in current_groups:
            if group.name not in (groups or []):
                client.role.groups.remove(group)
                self.stdout.write('Removed client from group %s' % group.name)

        if generate_password:
            return secret
