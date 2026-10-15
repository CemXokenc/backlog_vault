from django.test import TestCase
from django.urls import reverse

from vault.models import Developer, Game, Genre, Platform
from vault.roles import ensure_moderators_group
from vault.tests.helpers import (
    create_catalog,
    create_entry,
    create_gamer,
)


class CatalogPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.catalog = create_catalog()
        cls.regular = create_gamer("regular")
        cls.moderator = create_gamer("moderator", is_staff=True)
        cls.moderator.groups.add(ensure_moderators_group())
        cls.admin = create_gamer("boss", is_staff=True, is_superuser=True)

    def catalog_pages(self):
        game, genre = self.catalog.game, self.catalog.genre
        platform, developer = self.catalog.platform, self.catalog.developer
        return [
            ("vault:game-create", []),
            ("vault:game-update", [game.pk]),
            ("vault:game-delete", [game.pk]),
            ("vault:genre-create", []),
            ("vault:genre-update", [genre.pk]),
            ("vault:genre-delete", [genre.pk]),
            ("vault:platform-create", []),
            ("vault:platform-update", [platform.pk]),
            ("vault:platform-delete", [platform.pk]),
            ("vault:developer-create", []),
            ("vault:developer-update", [developer.pk]),
            ("vault:developer-delete", [developer.pk]),
        ]

    def test_regular_user_gets_403_on_every_catalog_action(self):
        self.client.force_login(self.regular)
        for name, args in self.catalog_pages():
            with self.subTest(page=name, method="GET"):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 403)
            with self.subTest(page=name, method="POST"):
                response = self.client.post(reverse(name, args=args), {})
                self.assertEqual(response.status_code, 403)

    def test_403_page_explains_what_happened(self):
        self.client.force_login(self.regular)
        response = self.client.get(reverse("vault:game-create"))
        self.assertContains(response, "don't have access", status_code=403)

    def test_regular_user_cannot_change_data(self):
        self.client.force_login(self.regular)
        self.client.post(
            reverse("vault:genre-delete", args=[self.catalog.genre.pk]),
        )
        self.client.post(
            reverse("vault:game-create"),
            {"title": "Sneaky", "release_year": 2020},
        )
        self.assertTrue(
            Genre.objects.filter(pk=self.catalog.genre.pk).exists()
        )
        self.assertFalse(Game.objects.filter(title="Sneaky").exists())

    def test_guest_is_sent_to_login(self):
        for name, args in self.catalog_pages():
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response["Location"])

    def test_moderator_and_admin_can_open_every_catalog_page(self):
        for gamer in (self.moderator, self.admin):
            self.client.force_login(gamer)
            for name, args in self.catalog_pages():
                with self.subTest(user=gamer.username, page=name):
                    response = self.client.get(reverse(name, args=args))
                    self.assertEqual(response.status_code, 200)

    def test_moderator_can_create_update_and_delete(self):
        self.client.force_login(self.moderator)
        game_data = {
            "title": "Moderated",
            "release_year": 2022,
            "genres": [self.catalog.genre.pk],
            "platforms": [self.catalog.platform.pk],
        }
        self.client.post(reverse("vault:game-create"), game_data)
        game = Game.objects.get(title="Moderated")
        self.client.post(
            reverse("vault:game-update", args=[game.pk]),
            {**game_data, "title": "Moderated 2"},
        )
        game.refresh_from_db()
        self.assertEqual(game.title, "Moderated 2")
        self.client.post(reverse("vault:game-delete", args=[game.pk]))
        self.assertFalse(Game.objects.filter(pk=game.pk).exists())

        self.client.post(reverse("vault:genre-create"), {"name": "Puzzle"})
        self.client.post(reverse("vault:platform-create"), {"name": "Switch"})
        self.client.post(
            reverse("vault:developer-create"),
            {"name": "Valve", "country": "USA"},
        )
        self.assertTrue(Genre.objects.filter(name="Puzzle").exists())
        self.assertTrue(Platform.objects.filter(name="Switch").exists())
        self.assertTrue(Developer.objects.filter(name="Valve").exists())

    def test_everyone_can_browse_the_catalog(self):
        self.client.force_login(self.regular)
        pages = [
            ("vault:game-list", []),
            ("vault:game-detail", [self.catalog.game.pk]),
        ]
        for name, args in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name, args=args))
                self.assertEqual(response.status_code, 200)

    def test_regular_user_keeps_library_and_collections(self):
        self.client.force_login(self.regular)
        game = self.catalog.game
        response = self.client.post(
            reverse("vault:library-create", args=[game.pk]),
            {"status": "planned", "hours_played": 0},
        )
        self.assertEqual(response.status_code, 302)
        response = self.client.post(
            reverse("vault:collection-create"),
            {"title": "Mine", "description": ""},
        )
        self.assertEqual(response.status_code, 302)
        entry = create_entry(self.moderator, game)
        response = self.client.get(
            reverse("vault:library-update", args=[entry.pk]),
        )
        self.assertEqual(response.status_code, 404)


class CatalogButtonsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.catalog = create_catalog()
        cls.regular = create_gamer("regular")
        cls.moderator = create_gamer("moderator", is_staff=True)
        cls.moderator.groups.add(ensure_moderators_group())

    def pages(self):
        return {
            "vault:game-list": (reverse("vault:game-create"),),
            "vault:genre-list": (
                reverse("vault:genre-create"),
                reverse("vault:genre-update", args=[self.catalog.genre.pk]),
                reverse("vault:genre-delete", args=[self.catalog.genre.pk]),
            ),
            "vault:platform-list": (
                reverse("vault:platform-create"),
                reverse(
                    "vault:platform-update", args=[self.catalog.platform.pk]
                ),
                reverse(
                    "vault:platform-delete", args=[self.catalog.platform.pk]
                ),
            ),
            "vault:developer-list": (
                reverse("vault:developer-create"),
                reverse(
                    "vault:developer-update",
                    args=[self.catalog.developer.pk],
                ),
                reverse(
                    "vault:developer-delete",
                    args=[self.catalog.developer.pk],
                ),
            ),
        }

    def test_regular_user_sees_no_catalog_buttons(self):
        self.client.force_login(self.regular)
        pages = {"vault:game-list": self.pages()["vault:game-list"]}
        for name, links in pages.items():
            response = self.client.get(reverse(name))
            for link in links:
                with self.subTest(page=name, link=link):
                    self.assertNotContains(response, f'href="{link}"')

    def test_moderator_sees_catalog_buttons(self):
        self.client.force_login(self.moderator)
        for name, links in self.pages().items():
            response = self.client.get(reverse(name))
            for link in links:
                with self.subTest(page=name, link=link):
                    self.assertContains(response, f'href="{link}"')

    def test_game_detail_buttons_follow_permissions(self):
        game = self.catalog.game
        update = reverse("vault:game-update", args=[game.pk])
        delete = reverse("vault:game-delete", args=[game.pk])
        url = reverse("vault:game-detail", args=[game.pk])
        self.client.force_login(self.regular)
        response = self.client.get(url)
        self.assertNotContains(response, f'href="{update}"')
        self.assertNotContains(response, f'href="{delete}"')
        self.client.force_login(self.moderator)
        response = self.client.get(url)
        self.assertContains(response, f'href="{update}"')
        self.assertContains(response, f'href="{delete}"')

    def test_regular_user_still_sees_library_actions(self):
        game = self.catalog.game
        url = reverse("vault:game-detail", args=[game.pk])
        self.client.force_login(self.regular)
        response = self.client.get(url)
        self.assertContains(
            response,
            reverse("vault:library-create", args=[game.pk]),
        )


class ReferenceAccessTests(TestCase):
    """Genres, platforms and developers are for moderators and admins."""

    PAGES = ("vault:genre-list", "vault:platform-list", "vault:developer-list")

    @classmethod
    def setUpTestData(cls):
        cls.regular = create_gamer("regular")
        cls.moderator = create_gamer("moderator", is_staff=True)
        cls.moderator.groups.add(ensure_moderators_group())

    def test_regular_user_gets_403_on_reference_lists(self):
        self.client.force_login(self.regular)
        for name in self.PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 403)

    def test_moderator_opens_reference_lists(self):
        self.client.force_login(self.moderator)
        for name in self.PAGES:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_regular_user_sees_no_reference_links(self):
        self.client.force_login(self.regular)
        for page in ("vault:index", "vault:game-list"):
            response = self.client.get(reverse(page))
            with self.subTest(page=page):
                self.assertNotContains(response, ">Reference<")
                for name in self.PAGES:
                    self.assertNotContains(response, reverse(name))

    def test_moderator_sees_reference_menu_and_tiles(self):
        self.client.force_login(self.moderator)
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, ">Reference</a>")
        for name in self.PAGES:
            self.assertContains(response, reverse(name))
