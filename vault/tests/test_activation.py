from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from vault.emails import build_activation_url, send_activation_email
from vault.tests.helpers import create_gamer


class ActivationEmailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer(
            "newbie",
            email="newbie@example.com",
            nickname="Newbie",
            is_active=False,
        )

    def request(self):
        return RequestFactory().get("/", HTTP_HOST="testserver")

    def test_email_contains_an_absolute_activation_link(self):
        send_activation_email(self.request(), self.gamer)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["newbie@example.com"])
        self.assertEqual(
            message.subject, "Activate your Backlog Vault account"
        )
        self.assertIn("Hi Newbie", message.body)
        self.assertIn(
            build_activation_url(self.request(), self.gamer),
            message.body,
        )
        self.assertIn("http://testserver/activate/", message.body)


class ActivationViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer(
            "newbie",
            email="newbie@example.com",
            is_active=False,
        )

    def link(self, gamer=None, token=None):
        gamer = gamer or self.gamer
        uid = urlsafe_base64_encode(force_bytes(gamer.pk))
        token = token or default_token_generator.make_token(gamer)
        return reverse(
            "vault:activate", kwargs={"uidb64": uid, "token": token}
        )

    def test_valid_link_activates_and_signs_in(self):
        response = self.client.get(self.link(), follow=True)
        self.assertRedirects(response, reverse("vault:index"))
        self.gamer.refresh_from_db()
        self.assertTrue(self.gamer.is_active)
        self.assertEqual(response.context["user"], self.gamer)
        self.assertContains(response, "Your account is active")

    def test_link_works_only_once(self):
        link = self.link()
        self.client.get(link)
        self.client.logout()
        response = self.client.get(link)
        self.assertEqual(response.status_code, 400)
        self.assertContains(
            response,
            "This activation link is not valid",
            status_code=400,
        )

    def test_tampered_token_is_rejected(self):
        response = self.client.get(self.link(token="abc-123456"))
        self.assertEqual(response.status_code, 400)
        self.gamer.refresh_from_db()
        self.assertFalse(self.gamer.is_active)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_garbage_user_id_is_rejected(self):
        url = reverse(
            "vault:activate",
            kwargs={"uidb64": "!!!", "token": "abc-123456"},
        )
        self.assertEqual(self.client.get(url).status_code, 400)

    def test_unknown_user_is_rejected(self):
        ghost = create_gamer("ghost")
        link = self.link(gamer=ghost)
        ghost.delete()
        self.assertEqual(self.client.get(link).status_code, 400)

    def test_token_of_another_gamer_does_not_work(self):
        other = create_gamer("other", is_active=False)
        token = default_token_generator.make_token(other)
        response = self.client.get(self.link(token=token))
        self.assertEqual(response.status_code, 400)
