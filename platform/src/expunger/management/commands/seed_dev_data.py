import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from expunger.models import Attorney, ExpungerProfile, Organization

PLSE_ORGANIZATION_NAME = "Philadelphia Lawyers for Social Equity"
DEFAULT_BAR_NUMBER = "000000"


class Command(BaseCommand):
    """
    Seed a development database with an Attorney and profile for the superuser
    created by `ensure_superuser`, so a fresh dev environment is usable
    immediately without a trip through the Django admin.

    Only ever run in development -- refuses with CommandError under any other
    settings module. Production seeds a superuser and nothing else, so that
    only real, manually created attorneys are selectable there.

    Reuses the PLSE Organization seeded by migration 0003 rather than creating
    a second one. Idempotent: keys on the OneToOneField from Attorney/
    ExpungerProfile to the user, so re-running does not create duplicates.
    """

    help = "Seed a development-only Attorney and profile for the superuser (dev environments only)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            default=None,
            help="Overrides the SUPERUSER_USERNAME environment variable.",
        )
        parser.add_argument(
            "--bar",
            default=DEFAULT_BAR_NUMBER,
            help=f"Bar number to set on the seeded Attorney (default: {DEFAULT_BAR_NUMBER}).",
        )

    def handle(self, *args, **options):
        if settings.ENVIRONMENT_NAME != "development":
            raise CommandError(
                "seed_dev_data only runs when ENVIRONMENT_NAME is 'development' "
                f"(got {settings.ENVIRONMENT_NAME!r}). Refusing to seed an Attorney "
                "outside development."
            )

        username = options["username"] or os.environ.get("SUPERUSER_USERNAME")
        if username is None or username.strip() == "":
            raise CommandError(
                "SUPERUSER_USERNAME is not set. Pass --username or set the environment variable."
            )

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(
                f"No user '{username}' exists. Run ensure_superuser first."
            )

        try:
            organization = Organization.objects.get(name=PLSE_ORGANIZATION_NAME)
        except Organization.DoesNotExist:
            raise CommandError(
                f"Organization '{PLSE_ORGANIZATION_NAME}' does not exist. "
                "It is expected to be seeded by migration 0003_auto_20190930_0311."
            )

        attorney, attorney_created = Attorney.objects.get_or_create(
            user=user, defaults={"bar": options["bar"]}
        )

        _, profile_created = ExpungerProfile.objects.get_or_create(
            user=user,
            defaults={"attorney": attorney, "organization": organization},
        )

        if attorney_created or profile_created:
            self.stdout.write(
                self.style.SUCCESS(f"Seeded dev Attorney/profile for '{username}'.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Dev Attorney/profile for '{username}' already present."
                )
            )
