from django.core import mail
from django.test import TestCase
from django.urls import reverse

from vault.forms import GamerCreationForm
from vault.models import Gamer
from vault.tests.helpers import PASSWORD, create_gamer


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


class RegistrationFlowTests(TestCase):
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

    def register(self, **extra):
        return self.client.post(
            reverse("vault:register"),
            self.data(**extra),
            follow=True,
        )

    def test_registration_creates_an_inactive_gamer(self):
        response = self.register()
        self.assertRedirects(response, reverse("vault:activation-sent"))
        gamer = Gamer.objects.get(username="newbie")
        self.assertFalse(gamer.is_active)
        self.assertEqual(gamer.nickname, "Newbie")
        self.assertTrue(gamer.check_password("Str0ng-pass-77"))

    def test_gamer_is_not_signed_in_after_registering(self):
        self.register()
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_confirmation_page_explains_how_to_activate(self):
        response = self.register()
        self.assertContains(response, "server console")
        self.assertContains(response, "moderator")

    def test_activation_email_is_sent(self):
        self.register()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["newbie@example.com"])
        self.assertIn("/activate/", mail.outbox[0].body)

    def test_invalid_registration_sends_nothing(self):
        response = self.register(email="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gamer.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_full_flow_through_the_emailed_link(self):
        self.register()
        body = mail.outbox[0].body
        link = next(line for line in body.splitlines() if "/activate/" in line)
        response = self.client.get(link, follow=True)
        self.assertRedirects(response, reverse("vault:index"))
        self.assertTrue(Gamer.objects.get(username="newbie").is_active)
        self.assertEqual(response.context["user"].username, "newbie")


class InactiveLoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer("sleepy", is_active=False)

    def login_errors(self):
        response = self.client.post(
            reverse("login"),
            {"username": "sleepy", "password": PASSWORD},
        )
        return [
            str(error) for error in response.context["form"].non_field_errors()
        ]

    def test_inactive_gamer_sees_a_clear_message(self):
        self.assertEqual(self.login_errors(), ["This account is inactive."])
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_wrong_password_still_gets_the_generic_message(self):
        response = self.client.post(
            reverse("login"),
            {"username": "sleepy", "password": "wrong"},
        )
        errors = response.context["form"].non_field_errors()
        self.assertIn("correct username and password", str(errors[0]))

    def test_moderator_activation_lets_the_gamer_in(self):
        admin = create_gamer("boss", is_staff=True, is_superuser=True)
        self.client.force_login(admin)
        self.client.post(
            reverse("admin:vault_gamer_changelist"),
            {"action": "activate_gamers", "_selected_action": [self.gamer.pk]},
        )
        self.client.logout()
        logged_in = self.client.login(username="sleepy", password=PASSWORD)
        self.assertTrue(logged_in)

    def test_deactivated_gamer_loses_the_existing_session(self):
        gamer = create_gamer("active_one")
        self.client.force_login(gamer)
        self.assertEqual(
            self.client.get(reverse("vault:library-list")).status_code, 200
        )
        gamer.is_active = False
        gamer.save()
        response = self.client.get(reverse("vault:library-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])
