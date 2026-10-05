from django.test import TestCase
from django.urls import reverse

from vault.models import LibraryEntry
from vault.tests.helpers import (
    create_catalog,
    create_entry,
    create_gamer,
)


class NextUrlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer()
        cls.catalog = create_catalog()
        cls.game = cls.catalog.game
        cls.entry = create_entry(cls.gamer, cls.game, status="playing")
        cls.game_url = reverse("vault:game-detail", args=[cls.game.pk])
        cls.update_url = reverse("vault:library-update", args=[cls.entry.pk])
        cls.delete_url = reverse("vault:library-delete", args=[cls.entry.pk])
        cls.form_data = {
            "status": "completed",
            "platform": cls.catalog.platform.pk,
            "hours_played": 12,
        }

    def setUp(self):
        self.client.force_login(self.gamer)

    def test_update_returns_to_next_url(self):
        response = self.client.post(
            f"{self.update_url}?next={self.game_url}",
            self.form_data,
        )
        self.assertRedirects(response, self.game_url)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.status, "completed")

    def test_update_without_next_goes_to_library(self):
        response = self.client.post(self.update_url, self.form_data)
        self.assertRedirects(response, reverse("vault:library-list"))

    def test_unsafe_next_is_ignored(self):
        response = self.client.post(
            f"{self.update_url}?next=https://evil.example/",
            self.form_data,
        )
        self.assertRedirects(response, reverse("vault:library-list"))

    def test_form_has_hidden_next_and_cancel_link(self):
        response = self.client.get(f"{self.update_url}?next={self.game_url}")
        self.assertContains(
            response,
            f'<input type="hidden" name="next" value="{self.game_url}">',
            html=True,
        )
        self.assertContains(response, f'href="{self.game_url}"')

    def test_delete_returns_to_next_url(self):
        response = self.client.post(f"{self.delete_url}?next={self.game_url}")
        self.assertRedirects(response, self.game_url)
        self.assertFalse(
            LibraryEntry.objects.filter(pk=self.entry.pk).exists()
        )

    def test_create_returns_to_game_by_default(self):
        self.entry.delete()
        url = reverse("vault:library-create", args=[self.game.pk])
        response = self.client.post(url, self.form_data)
        self.assertRedirects(response, self.game_url)

    def test_create_returns_to_next_url(self):
        self.entry.delete()
        url = reverse("vault:library-create", args=[self.game.pk])
        response = self.client.post(f"{url}?next=/library/", self.form_data)
        self.assertRedirects(response, reverse("vault:library-list"))
