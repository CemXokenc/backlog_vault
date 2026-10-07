from django.test import TestCase
from django.urls import reverse

from vault.models import Game
from vault.tests.helpers import (
    create_collection,
    create_entry,
    create_gamer,
    create_moderator,
)


def create_covered_games(count):
    return [
        Game.objects.create(
            title=f"Covered {number}",
            release_year=2020,
            cover_url=f"https://example.com/cover-{number}.jpg",
        )
        for number in range(count)
    ]


class PageHeaderTests(TestCase):
    def test_list_pages_have_a_page_header(self):
        self.client.force_login(create_moderator("mod"))
        pages = (
            "vault:game-list",
            "vault:collection-list",
            "vault:library-list",
            "vault:gamer-list",
            "vault:genre-list",
            "vault:platform-list",
            "vault:developer-list",
        )
        for name in pages:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, 'class="page-header"')

    def test_empty_lists_show_an_empty_state(self):
        self.client.force_login(create_gamer("alex"))
        for name in ("vault:game-list", "vault:collection-list"):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, "empty-state")


class CollectionMosaicTests(TestCase):
    def setUp(self):
        self.owner = create_gamer("owner")
        self.client.force_login(self.owner)

    def mosaic(self):
        html = self.client.get(reverse("vault:collection-list")).content
        html = html.decode()
        start = html.index("collection-mosaic")
        return html[start : html.index("card-body", start)]

    def test_mosaic_shows_at_most_four_covers(self):
        create_collection(self.owner, games=create_covered_games(6))
        self.assertEqual(self.mosaic().count("<img"), 4)

    def test_empty_collection_has_a_placeholder(self):
        create_collection(self.owner)
        self.assertIn("collection-mosaic-empty", self.mosaic())

    def test_game_without_cover_gets_an_empty_tile(self):
        game = Game.objects.create(title="Plain", release_year=2020)
        create_collection(self.owner, games=[game])
        self.assertIn("tile-empty", self.mosaic())


class LibraryAndProfileTests(TestCase):
    def setUp(self):
        self.gamer = create_gamer("zed", nickname="zed")
        self.client.force_login(self.gamer)

    def test_library_rows_show_a_cover_thumbnail(self):
        game = create_covered_games(1)[0]
        create_entry(self.gamer, game)
        response = self.client.get(reverse("vault:library-list"))
        self.assertContains(response, 'class="game-thumb"')
        self.assertContains(response, game.cover_url)

    def test_library_row_without_cover_has_a_placeholder(self):
        game = Game.objects.create(title="Plain", release_year=2020)
        create_entry(self.gamer, game)
        response = self.client.get(reverse("vault:library-list"))
        self.assertContains(response, "game-thumb-empty")

    def test_gamer_cards_show_an_initial_avatar(self):
        response = self.client.get(reverse("vault:gamer-list"))
        self.assertContains(response, '<span class="avatar">Z</span>')

    def test_profile_has_a_hero_with_actions_for_the_owner(self):
        url = reverse("vault:gamer-detail", args=[self.gamer.pk])
        response = self.client.get(url)
        self.assertContains(response, "profile-hero")
        self.assertContains(response, "Edit profile")

    def test_profile_of_someone_else_has_no_edit_button(self):
        other = create_gamer("other")
        url = reverse("vault:gamer-detail", args=[other.pk])
        response = self.client.get(url)
        self.assertContains(response, "profile-hero")
        self.assertNotContains(response, "Edit profile")


class ErrorAndAuthPageTests(TestCase):
    def test_404_page_shows_the_big_code(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "error-code", status_code=404)

    def test_login_and_register_have_the_icon_header(self):
        for name in ("login", "vault:register"):
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertContains(response, "auth-icon")
