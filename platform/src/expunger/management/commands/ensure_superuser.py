import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """
    Create or update the app's superuser account to match the given credentials.

    Idempotent, and safe to run on every deploy: the account is created if it does
    not exist, and its password, staff, and superuser flags are reset to match on
    every run. That makes the backend secret the source of truth for the admin
    login rather than a one-time seed -- rotating the admin password is done by
    resealing SUPERUSER_PASSWORD and redeploying, not by any manual step against
    the cluster.

    Because the account is looked up by username, rotating SUPERUSER_USERNAME
    instead of the password leaves the old username as a live superuser account
    with its old password. Rotate the password, not the username.

    This command creates no Attorney record. In production only manually created,
    real attorneys should be selectable; the development-only equivalent that also
    seeds an Attorney and profile is `seed_dev_data`.
    """

    help = "Create or update the superuser account from SUPERUSER_USERNAME/SUPERUSER_PASSWORD."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=None,
            help="Overrides the SUPERUSER_USERNAME environment variable.",
        )
        parser.add_argument(
            "--password",
            default=None,
            help=(
                "Overrides the SUPERUSER_PASSWORD environment variable. Intended for "
                "tests -- passing a password on the command line leaks it into shell "
                "history and process listings, so real deployments should rely on the "
                "environment variable instead."
            ),
        )
        parser.add_argument(
            "--first-name",
            default="PLSE",
            help="First name to set on the account (default: PLSE).",
        )
        parser.add_argument(
            "--last-name",
            default="Admin",
            help="Last name to set on the account (default: Admin).",
        )

    def handle(self, *args, **options):
        username = options["username"] or os.environ.get("SUPERUSER_USERNAME")
        password = options["password"] or os.environ.get("SUPERUSER_PASSWORD")

        if username is None or username.strip() == "":
            raise CommandError(
                "SUPERUSER_USERNAME is not set. Refusing to create a superuser "
                "with a blank username."
            )

        if password is None or password.strip() == "":
            raise CommandError(
                "SUPERUSER_PASSWORD is not set. Refusing to create a superuser "
                "with a blank password."
            )

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)

        user.set_password(password)
        user.first_name = options["first_name"]
        user.last_name = options["last_name"]
        user.is_staff = True
        user.is_superuser = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{username}'."))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Updated existing superuser '{username}'.")
            )
