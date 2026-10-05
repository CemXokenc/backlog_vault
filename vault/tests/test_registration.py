from django.test import TestCase
from django.urls import reverse

from vault.forms import GamerCreationForm
from vault.models import Gamer
from vault.tests.helpers import create_gamer


class RegistrationFormTests(TestCase):
    def data(self, **extra):
        data = {
            "username": "newbie",
            "email": "newbie@example.com",
            "password1": "Str0ng-pass-77",
            "password2": "Str0ng-pass-77",
            "nickname": "Newbie",
        }
        data.update(extra)
        return data

    def test_valid_form(self):
        self.assertTrue(GamerCreationForm(self.data()).is_valid())

    def test_email_is_required(self):
        form = GamerCreationForm(self.data(email=""))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_must_be_valid(self):
        form = GamerCreationForm(self.data(email="not-an-email"))
        self.assertIn("email", form.errors)

    def test_email_must_be_unique_ignoring_case(self):
        create_gamer("taken", email="Taken@Example.com")
        form = GamerCreationForm(self.data(email="taken@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("already exists", form.errors["email"][0])

    def test_users_without_email_do_not_block_registration(self):
        create_gamer("old_user")
        self.assertTrue(GamerCreationForm(self.data()).is_valid())

    def test_register_page_shows_the_email_field(self):
        response = self.client.get(reverse("vault:register"))
        self.assertContains(response, 'name="email"')
        self.assertEqual(Gamer.objects.count(), 0)
