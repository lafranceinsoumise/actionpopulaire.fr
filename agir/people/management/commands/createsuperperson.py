import sys
import os
import getpass

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.core import exceptions
from django.utils.text import capfirst
from django.utils.encoding import force_str
from django.contrib.auth.password_validation import validate_password

from ...models import Person, PersonEmail


class NotRunningInTTYException(Exception):
    pass


class Command(BaseCommand):
    help = "Used to create a superuser."
    requires_migrations_checks = True

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.email_field = PersonEmail._meta.get_field("address")

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            dest="email",
            default=None,
            help="Specifies the login for the superuser.",
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            default=True,
            help=(
                "Tells Django to NOT prompt the user for input of any kind. "
                "You must use --email with --noinput, along with an option for "
                "any other required field. Superusers created with --noinput will "
                "not be able to log in until they're given a valid password."
            ),
        )
        parser.add_argument(
            "--database",
            action="store",
            dest="database",
            default=DEFAULT_DB_ALIAS,
            help='Specifies the database to use. Default is "default".',
        )

    def handle(self, *args, **options):
        email = options["email"]
        database = options["database"]

        # If not provided, create the user with an unusable password
        password = None
        user_data = {}
        # Same as user_data but with foreign keys as fake model instances
        # instead of raw IDs.
        fake_user_data = {}

        # Do quick and dirty validation if --noinput
        if not options["interactive"]:
            try:
                if not email:
                    raise CommandError("You must use --email with --noinput.")
                email = self.email_field.clean(email, None)

            except exceptions.ValidationError as e:
                raise CommandError("; ".join(e.messages))

            password = os.environ.get("SUPERPERSON_PASSWORD", None)

        else:
            try:
                if hasattr(sys.stdin, "isatty") and not sys.stdin.isatty():
                    raise NotRunningInTTYException("Not running in a TTY")

                # Get a username
                verbose_field_name = self.email_field.verbose_name
                while email is None:
                    input_msg = capfirst(verbose_field_name)
                    username_rel = self.email_field.remote_field
                    input_msg = force_str(
                        "%s%s: "
                        % (
                            input_msg,
                            (
                                " (%s.%s)"
                                % (
                                    username_rel.model._meta.object_name,
                                    username_rel.field_name,
                                )
                                if username_rel
                                else ""
                            ),
                        )
                    )
                    email = self.get_input_data(self.email_field, input_msg)
                    if not email:
                        continue
                    if self.email_field.unique:
                        try:
                            Person._default_manager.db_manager(
                                database
                            ).get_by_natural_key(email)
                        except Person.DoesNotExist:
                            pass
                        else:
                            self.stderr.write(
                                "Error: That %s is already taken." % verbose_field_name
                            )
                            email = None

                # Get a password
                while password is None:
                    password = getpass.getpass()
                    password2 = getpass.getpass(force_str("Password (again): "))
                    if password != password2:
                        self.stderr.write("Error: Your passwords didn't match.")
                        password = None
                        # Don't validate passwords that don't match.
                        continue

                    if password.strip() == "":
                        self.stderr.write("Error: Blank passwords aren't allowed.")
                        password = None
                        # Don't validate blank passwords.
                        continue

                    try:
                        validate_password(password2, Person(**fake_user_data))
                    except exceptions.ValidationError as err:
                        self.stderr.write("\n".join(err.messages))
                        password = None

            except KeyboardInterrupt:
                self.stderr.write("\nOperation cancelled.")
                sys.exit(1)

            except NotRunningInTTYException:
                self.stdout.write(
                    "Superuser creation skipped due to not running in a TTY. "
                    "You can run `manage.py createsuperuser` in your project "
                    "to create one manually."
                )

        if email:
            user_data["email"] = email
            user_data["password"] = password
            Person._default_manager.db_manager(database).create_superperson(**user_data)
            if options["verbosity"] >= 1:
                self.stdout.write("Superuser created successfully.")

    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == "":
            raw_value = default
        try:
            val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % "; ".join(e.messages))
            val = None

        return val
