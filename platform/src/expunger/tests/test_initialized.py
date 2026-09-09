from django.test import TestCase
from django.contrib.auth.models import Group


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
