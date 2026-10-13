import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from expunger.models import Attorney

User = get_user_model()

# ensure_superuser falls back to these env vars when --username/--password are
# not given. This decorator clears those env vars for a test, so that we can
# test behavior when username or password are fully missing.
_no_superuser_env = mock.patch.dict(
    os.environ, {"SUPERUSER_USERNAME": "", "SUPERUSER_PASSWORD": ""}
)


class TestEnsureSuperuser(TestCase):
    def test_creates_superuser_when_absent(self):
        call_command("ensure_superuser", username="plse", password="a-password")

        user = User.objects.get(username="plse")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("a-password"))

    def test_sets_first_and_last_name(self):
        call_command(
            "ensure_superuser",
            username="plse",
            password="a-password",
            first_name="Jane",
            last_name="Doe",
        )

        user = User.objects.get(username="plse")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Doe")

    def test_second_run_does_not_duplicate(self):
        call_command("ensure_superuser", username="plse", password="a-password")
        call_command("ensure_superuser", username="plse", password="a-password")

        self.assertEqual(User.objects.filter(username="plse").count(), 1)

    def test_second_run_resets_the_password(self):
        call_command("ensure_superuser", username="plse", password="first-password")
        call_command("ensure_superuser", username="plse", password="second-password")

        user = User.objects.get(username="plse")
        self.assertFalse(user.check_password("first-password"))
        self.assertTrue(user.check_password("second-password"))

    def test_promotes_a_pre_existing_non_staff_user(self):
        User.objects.create_user(username="plse", password="old-password")

        call_command("ensure_superuser", username="plse", password="new-password")

        user = User.objects.get(username="plse")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("new-password"))

    def test_creates_no_attorney(self):
        before = Attorney.objects.count()

        call_command("ensure_superuser", username="plse", password="a-password")

        self.assertEqual(Attorney.objects.count(), before)

    @_no_superuser_env
    def test_raises_on_missing_username(self):
        with self.assertRaises(CommandError):
            call_command("ensure_superuser", username=None, password="a-password")

    def test_raises_on_blank_username(self):
        with self.assertRaises(CommandError):
            call_command("ensure_superuser", username="   ", password="a-password")

    @_no_superuser_env
    def test_raises_on_missing_password(self):
        with self.assertRaises(CommandError):
            call_command("ensure_superuser", username="plse", password=None)

    def test_raises_on_blank_password(self):
        with self.assertRaises(CommandError):
            call_command("ensure_superuser", username="plse", password="   ")
