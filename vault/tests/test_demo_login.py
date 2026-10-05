from django.test import TestCase, override_settings
from django.urls import reverse

from vault.roles import DEMO_USERS
from vault.tests.helpers import create_catalog, create_gamer, create_moderator


class DemoLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_gamer(DEMO_USERS["admin"], is_staff=True, is_superuser=True)
        create_moderator(DEMO_USERS["moderator"])
        create_gamer(DEMO_USERS["user"])
        cls.catalog = create_catalog()

    def sign_in_as(self, role):
        return self.client.post(
            reverse("vault:demo-login", args=[role]),
            follow=True,
        )

    def current_username(self, response):
        return response.context["user"].username

    @override_settings(DEMO_MODE=True)
    def test_each_role_signs_in_as_the_demo_user(self):
        for role, username in DEMO_USERS.items():
            with self.subTest(role=role):
                response = self.sign_in_as(role)
                self.assertRedirects(response, reverse("vault:index"))
                self.assertEqual(self.current_username(response), username)
                self.assertContains(response, f"signed in as {username}")

    @override_settings(DEMO_MODE=True)
    def test_roles_have_different_powers(self):
        create_url = reverse("vault:game-create")
        admin_url = reverse("admin:index")
        expected = {
            "admin": (200, 200),
            "moderator": (200, 200),
            "user": (403, 302),
        }
        for role, (create_status, admin_status) in expected.items():
            with self.subTest(role=role):
                self.sign_in_as(role)
                self.assertEqual(
                    self.client.get(create_url).status_code, create_status
                )
                self.assertEqual(
                    self.client.get(admin_url).status_code, admin_status
                )

    @override_settings(DEMO_MODE=True)
    def test_demo_login_requires_post(self):
        url = reverse("vault:demo-login", args=["admin"])
        self.assertEqual(self.client.get(url).status_code, 405)

    @override_settings(DEMO_MODE=True)
    def test_unknown_role_is_404(self):
        response = self.client.post(reverse("vault:demo-login", args=["root"]))
        self.assertEqual(response.status_code, 404)

    @override_settings(DEMO_MODE=False)
    def test_demo_login_is_disabled_outside_demo_mode(self):
        for role in DEMO_USERS:
            with self.subTest(role=role):
                response = self.client.post(
                    reverse("vault:demo-login", args=[role]),
                )
                self.assertEqual(response.status_code, 404)
        self.assertNotIn("_auth_user_id", self.client.session)

    @override_settings(DEMO_MODE=True)
    def test_header_shows_demo_menu_for_guests(self):
        response = self.client.get(reverse("login"))
        for role in DEMO_USERS:
            self.assertContains(
                response,
                reverse("vault:demo-login", args=[role]),
            )

    @override_settings(DEMO_MODE=False)
    def test_header_hides_demo_menu_outside_demo_mode(self):
        response = self.client.get(reverse("login"))
        self.assertNotContains(response, "demo-login")
        self.assertNotContains(response, "Sign in as")
