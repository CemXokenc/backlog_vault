from django.test import TestCase
from django.urls import reverse

from vault.tests.helpers import (
    create_catalog,
    create_collection,
    create_gamer,
)


class GuestGamePagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.catalog = create_catalog()
        cls.game = cls.catalog.game
        cls.owner = create_gamer("owner")
        cls.collection = create_collection(cls.owner, games=[cls.game])

    def test_guest_sees_catalog_with_search_and_filters(self):
        url = reverse("vault:game-list")
        response = self.client.get(url)
        self.assertContains(response, self.game.title)
        response = self.client.get(url + "?query=had")
        self.assertContains(response, self.game.title)

    def test_guest_sees_game_page(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.game.title)

    def test_guest_gets_login_hint_instead_of_actions(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertContains(response, "to add this game to your library")
        self.assertNotContains(
            response,
            reverse("vault:library-create", args=[self.game.pk]),
        )
        self.assertNotContains(response, "Add to collection")
        self.assertNotContains(response, self.collection.get_absolute_url())

    def test_guest_cannot_open_other_sections(self):
        pages = [
            reverse("vault:library-list"),
            reverse("vault:collection-list"),
            self.collection.get_absolute_url(),
            reverse("vault:gamer-list"),
            reverse("vault:gamer-detail", args=[self.owner.pk]),
            reverse("vault:genre-list"),
            reverse("vault:platform-list"),
            reverse("vault:developer-list"),
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response["Location"])
