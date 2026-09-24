import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

User = get_user_model()

# check_superuser_seeded falls back to this env var when --username is not given.
# compose.yaml sets it by default for the whole backend container pytest runs
# inside, so tests exercising the missing-username case must clear it first.
_no_superuser_env = mock.patch.dict(os.environ, {"SUPERUSER_USERNAME": ""})


class TestCheckSuperuserSeeded(TestCase):
    def test_passes_for_a_working_superuser(self):
        User.objects.create_superuser(username="plse", password="a-password")

        call_command("check_superuser_seeded", username="plse")

    def test_raises_when_user_does_not_exist(self):
        with self.assertRaises(CommandError):
            call_command("check_superuser_seeded", username="plse")

    def test_raises_when_not_staff(self):
        user = User.objects.create_superuser(username="plse", password="a-password")
        user.is_staff = False
        user.save()

        with self.assertRaises(CommandError):
            call_command("check_superuser_seeded", username="plse")

    def test_raises_when_not_superuser(self):
        user = User.objects.create_user(username="plse", password="a-password")
        user.is_staff = True
        user.is_superuser = False
        user.save()

        with self.assertRaises(CommandError):
            call_command("check_superuser_seeded", username="plse")

    @_no_superuser_env
    def test_raises_on_missing_username(self):
        with self.assertRaises(CommandError):
            call_command("check_superuser_seeded", username=None)
