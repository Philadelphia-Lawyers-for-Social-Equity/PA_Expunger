import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Verify that SUPERUSER_USERNAME resolves to a working staff/superuser account.

    Used by CI to confirm the migration Job's `ensure_superuser` invocation actually
    ran against the deployed database, rather than only unit-testing the command in
    isolation. Does not create or modify anything.
    """

    help = "Check that SUPERUSER_USERNAME is a staff/superuser account."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=None,
            help="Overrides the SUPERUSER_USERNAME environment variable.",
        )

    def handle(self, *args, **options):
        username = options["username"] or os.environ.get("SUPERUSER_USERNAME")
        if username is None or username.strip() == "":
            raise CommandError(
                "SUPERUSER_USERNAME is not set. Pass --username or set the environment variable."
            )

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"No user '{username}' exists.")

        if not user.is_staff:
            raise CommandError(f"'{username}' is not staff.")

        if not user.is_superuser:
            raise CommandError(f"'{username}' is not a superuser.")

        self.stdout.write(
            self.style.SUCCESS(f"OK: '{username}' is a working superuser.")
        )
