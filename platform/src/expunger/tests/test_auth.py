from django.test import Client, TestCase
from django.urls import reverse

from expunger import factories


class TestTokens(TestCase):
    """Test the JWT lifecycle the frontend relies on"""

    def setUp(self):
        self.password = factories.random_text(8)
        self.user = factories.UserFactory(password=self.password)
        self.client = Client()

    def obtain_tokens(self):
        res = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.user.username, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)

        return res.json()

    def test_login_produces_a_token_pair(self):
        """Logging in returns both tokens, since the frontend stores and refreshes them"""
        tokens = self.obtain_tokens()

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_refresh_produces_a_usable_access_token(self):
        """The refresh token buys a new access token that authenticates a request"""
        tokens = self.obtain_tokens()
        res = self.client.post(
            reverse("token_refresh"),
            {"refresh": tokens["refresh"]},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        access = res.json()["access"]

        res = self.client.get(
            reverse("expunger:organizations"),
            headers={"authorization": f"Bearer {access}"},
        )
        self.assertEqual(res.status_code, 200)

    def test_refresh_rejects_an_invalid_token(self):
        """A refresh token that isn't ours is rejected, which logs the frontend out"""
        res = self.client.post(
            reverse("token_refresh"),
            {"refresh": "not-a-real-token"},
            content_type="application/json",
        )

        self.assertEqual(res.status_code, 401)
