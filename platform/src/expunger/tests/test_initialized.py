# -*- coding: utf-8 -*-
import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


class TestSuperUserExists(TestCase):
    """
    App data migrations must build the EXPUNGER_USER
    """
    def test_expunger_user_is_ready(self):
        name = os.environ["EXPUNGER_USER"]

        User = get_user_model()
        root = User.objects.get(username=name)

        self.assertTrue(root.is_staff)
        self.assertTrue(root.is_superuser)


class TestGroupsExist(TestCase):
    """
    App data migrations must provide expected user groups.
    """
    def test_laywers_exist(self):
        """The 'attorney' group must exist, and have expected permissions"""
        Group.objects.get(name="Attorney")

    def test_interns_exist(self):
        """The 'intern' group must exist, and have expected permissions"""
        Group.objects.get(name="Intern")

    def test_volunteers_exist(self):
        """The 'volunteer' group must exist, and have expected permissions"""
        Group.objects.get(name="Volunteer")
