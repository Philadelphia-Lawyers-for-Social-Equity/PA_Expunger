from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from expunger.models import Attorney, ExpungerProfile, Organization

User = get_user_model()


class TestSeedDevData(TestCase):
    def setUp(self):
        call_command("ensure_superuser", username="plse", password="a-password")

    @override_settings(ENVIRONMENT_NAME="development")
    def test_creates_attorney_and_profile(self):
        call_command("seed_dev_data", username="plse")

        user = User.objects.get(username="plse")
        attorney = Attorney.objects.get(user=user)
        profile = ExpungerProfile.objects.get(user=user)

        self.assertEqual(profile.attorney, attorney)
        self.assertEqual(
            profile.organization.name, "Philadelphia Lawyers for Social Equity"
        )

    @override_settings(ENVIRONMENT_NAME="development")
    def test_reuses_the_seeded_plse_organization(self):
        before = Organization.objects.filter(
            name="Philadelphia Lawyers for Social Equity"
        ).count()

        call_command("seed_dev_data", username="plse")

        after = Organization.objects.filter(
            name="Philadelphia Lawyers for Social Equity"
        ).count()
        self.assertEqual(before, after)

    @override_settings(ENVIRONMENT_NAME="development")
    def test_second_run_does_not_duplicate(self):
        call_command("seed_dev_data", username="plse")
        call_command("seed_dev_data", username="plse")

        user = User.objects.get(username="plse")
        self.assertEqual(Attorney.objects.filter(user=user).count(), 1)
        self.assertEqual(ExpungerProfile.objects.filter(user=user).count(), 1)

    @override_settings(ENVIRONMENT_NAME="production")
    def test_refuses_outside_development(self):
        with self.assertRaises(CommandError):
            call_command("seed_dev_data", username="plse")

        user = User.objects.get(username="plse")
        self.assertFalse(Attorney.objects.filter(user=user).exists())

    @override_settings(ENVIRONMENT_NAME="development")
    def test_raises_when_superuser_does_not_exist(self):
        with self.assertRaises(CommandError):
            call_command("seed_dev_data", username="not-plse")
