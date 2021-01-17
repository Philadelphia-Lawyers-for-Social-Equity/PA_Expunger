# -*- coding: utf-8 -*-
from django.test import Client, TestCase
from django.urls import reverse

from expunger import factories


class Authenticated:
    """Provide an authenticated client for Tests"""

    @staticmethod
    def logged_in_client(user=None):
        pw = factories.random_text(8)

        if user is None:
            user = factories.UserFactory()

        user.set_password(pw)
        user.save()

        client = Client()
        success = client.login(username=user.username, password=pw)

        if not success:
            raise RuntimeError("Failed to produce authenticated client")

        return client

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        super().setUpClass(*args, **kwargs)

        profile = factories.ExpungerProfileFactory()
        client = cls.logged_in_client(profile.user)
        cls.authenticated_profile = profile
        cls.authenticated_client = client


class TestRest(Authenticated, TestCase):
    """Test the JSON API"""

    def test_read_organization(self):
        """API shows a single organization"""
        org = factories.OrganizationFactory()
        url = reverse("expunger:organization-detail", kwargs={"pk": org.pk})
        res = self.authenticated_client.get(url)
        jsr = res.json()

        self.assertEqual(jsr["name"], org.name)
        self.assertEqual(jsr["phone"], org.phone)
        self.assertEqual(jsr["address"]["street1"], org.address.street1)
        self.assertEqual(jsr["address"]["city"], org.address.city)
        self.assertEqual(jsr["address"]["state"], org.address.state)
        self.assertEqual(jsr["address"]["zipcode"], org.address.zipcode)

    def test_read_attorney(self):
        """API shows a single attortey"""
        attorney = factories.AttorneyFactory()
        url = reverse("expunger:attorney-detail", kwargs={"pk": attorney.pk})
        res = self.authenticated_client.get(url)
        jsr = res.json()

        self.assertEqual(jsr["name"], "%s %s" % (
            attorney.user.first_name, attorney.user.last_name))
        self.assertEqual(jsr["bar"], attorney.bar)

    def test_my_profile(self):
        """API allows user to review their own profile"""
        url = reverse("expunger:my-profile")
        res = self.authenticated_client.get(url)
        jsr = res.json()

        self.assertEqual(jsr["user"]["first_name"],
                         self.authenticated_profile.user.first_name)
        self.assertEqual(jsr["user"]["last_name"],
                         self.authenticated_profile.user.last_name)
        self.assertEqual(jsr["user"]["username"],
                         self.authenticated_profile.user.username)
        self.assertEqual(jsr["user"]["email"],
                         self.authenticated_profile.user.email)

        self.assertEqual(jsr["attorney"]["pk"],
                         self.authenticated_profile.attorney.pk)
        self.assertEqual(jsr["organization"]["pk"],
                         self.authenticated_profile.organization.pk)

    def test_create_my_profile(self):
        """API allows user to create a profile, if needed"""
        url = reverse("expunger:my-profile")
        user = factories.UserFactory()
        client = self.logged_in_client(user)

        organization = factories.OrganizationFactory()
        attorney = factories.AttorneyFactory()

        res = client.post(
            url, {"attorney": attorney.pk, "organization": organization.pk})
        jsr = res.json()
        self.assertEqual(res.status_code, 201)

        self.assertEqual(jsr["attorney"]["pk"], attorney.pk)
        self.assertEqual(jsr["organization"]["pk"], organization.pk)

        self.assertEqual(user.expungerprofile.attorney.pk, attorney.pk)
        self.assertEqual(user.expungerprofile.organization.pk, organization.pk)

    def test_update_my_profile(self):
        """API allows user to update their profile"""
        url = reverse("expunger:my-profile")
        new_attorney = factories.AttorneyFactory()
        new_org = factories.OrganizationFactory()

        self.assertNotEqual(new_attorney, self.authenticated_profile.attorney)
        self.assertNotEqual(new_org, self.authenticated_profile.organization)

        res = self.authenticated_client.put(
            url,
            {"attorney": new_attorney.pk},
            content_type="application/json")
        jsr = res.json()

        self.authenticated_profile.refresh_from_db()

        self.assertEqual(res.status_code, 200, msg=jsr)
        self.assertEqual(jsr["attorney"]["pk"], new_attorney.pk, msg=jsr)
        self.assertEqual(self.authenticated_profile.attorney, new_attorney)

        res = self.authenticated_client.put(
            url, {"organization": new_org.pk}, content_type="application/json")
        jsr = res.json()

        self.authenticated_profile.refresh_from_db()

        self.assertEqual(res.status_code, 200, msg=jsr)
        self.assertEqual(jsr["organization"]["pk"], new_org.pk)
        self.assertEqual(self.authenticated_profile.organization,
                         new_org)
