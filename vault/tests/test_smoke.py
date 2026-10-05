from django.test import TestCase
from django.urls import reverse

from vault.models import Game

from vault.tests.helpers import (
    create_catalog,
    create_collection,
    create_entry,
    create_gamer,
)


class SmokeTests(TestCase):
    """Every page must open for a logged-in user and redirect guests."""

    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_gamer()
        cls.catalog = create_catalog()
        cls.game = cls.catalog.game
        cls.entry = create_entry(cls.gamer, cls.game, status="playing")
        cls.collection = create_collection(cls.gamer, games=[cls.game])

    def pages(self):
        game_pk = self.game.pk
        return [
            ("vault:index", []),
            ("vault:game-list", []),
            ("vault:game-detail", [game_pk]),
            ("vault:game-create", []),
            ("vault:game-update", [game_pk]),
            ("vault:game-delete", [game_pk]),
            ("vault:genre-list", []),
            ("vault:genre-create", []),
            ("vault:genre-update", [self.catalog.genre.pk]),
            ("vault:genre-delete", [self.catalog.genre.pk]),
            ("vault:platform-list", []),
            ("vault:platform-create", []),
            ("vault:platform-update", [self.catalog.platform.pk]),
            ("vault:platform-delete", [self.catalog.platform.pk]),
            ("vault:developer-list", []),
            ("vault:developer-create", []),
            ("vault:developer-update", [self.catalog.developer.pk]),
            ("vault:developer-delete", [self.catalog.developer.pk]),
            ("vault:library-list", []),
            ("vault:library-update", [self.entry.pk]),
            ("vault:library-delete", [self.entry.pk]),
            ("vault:collection-list", []),
            ("vault:collection-detail", [self.collection.pk]),
            ("vault:collection-create", []),
            ("vault:collection-update", [self.collection.pk]),
            ("vault:collection-delete", [self.collection.pk]),
            ("vault:gamer-list", []),
            ("vault:gamer-detail", [self.gamer.pk]),
            ("vault:gamer-update", [self.gamer.pk]),
        ]

    def test_pages_open_for_logged_in_user(self):
        self.client.force_login(self.gamer)
        for name, args in self.pages():
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)

    def test_pages_redirect_guests_to_login(self):
        for name, args in self.pages():
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response["Location"])

    def test_library_create_page_opens(self):
        self.client.force_login(self.gamer)
        other = Game.objects.create(
            title="Other",
            release_year=2021,
        )
        other.platforms.add(self.catalog.platform)
        url = reverse("vault:library-create", args=[other.pk])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_list_pages_accept_search_and_filters(self):
        self.client.force_login(self.gamer)
        game_list = reverse("vault:game-list")
        queries = [
            "?query=had",
            f"?genre={self.catalog.genre.pk}",
            f"?platform={self.catalog.platform.pk}",
            "?page=1",
            "?page=999",
        ]
        for query in queries:
            with self.subTest(query=query):
                response = self.client.get(game_list + query)
                self.assertIn(response.status_code, (200, 404))
        for name in ("genre", "platform", "developer", "collection", "gamer"):
            with self.subTest(search=name):
                url = reverse(f"vault:{name}-list") + "?query=a"
                self.assertEqual(self.client.get(url).status_code, 200)
