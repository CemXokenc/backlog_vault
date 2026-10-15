from django.test import TestCase
from django.urls import reverse

from vault.models import Game
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


class GuestHomePageTests(TestCase):
    def test_guest_home_explains_what_is_available(self):
        response = self.client.get(reverse("vault:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "only the game catalog is available")
        self.assertContains(response, reverse("login"))
        self.assertContains(response, reverse("vault:register"))
        self.assertNotContains(response, "Welcome back")

    def test_guest_navbar_shows_only_the_catalog(self):
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, 'href="/games/"')
        self.assertNotContains(response, 'href="/collections/"')
        self.assertNotContains(response, 'href="/library/"')

    def test_gamer_still_sees_the_dashboard(self):
        self.client.force_login(create_gamer("alex"))
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, "Welcome back")
        self.assertNotContains(response, "only the game catalog")


class GuestLandingTests(TestCase):
    def make_covered_games(self, count):
        for number in range(count):
            Game.objects.create(
                title=f"Game {number}",
                release_year=2020,
                cover_url=f"https://example.com/cover-{number}.jpg",
            )

    def test_landing_works_on_an_empty_database(self):
        response = self.client.get(reverse("vault:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "cover-wall")
        self.assertNotContains(response, "Popular right now")

    def test_landing_shows_stats_features_and_register_call(self):
        create_catalog()
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, "How it works")
        self.assertContains(response, 'data-target="1"')
        self.assertContains(response, reverse("vault:register"))

    def test_landing_lists_popular_games(self):
        game = create_catalog().game
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, "Popular right now")
        self.assertContains(response, game.title)

    def test_cover_wall_needs_enough_covers(self):
        self.make_covered_games(5)
        response = self.client.get(reverse("vault:index"))
        self.assertNotContains(response, "cover-wall")

    def test_cover_wall_has_three_looping_rows(self):
        self.make_covered_games(6)
        html = self.client.get(reverse("vault:index")).content.decode()
        self.assertEqual(html.count('class="cover-row'), 3)
        self.assertEqual(html.count("cover-row-reverse"), 1)
        # Every row holds its 8 covers twice, so the animation can loop.
        wall = html[
            html.index("cover-wall") : html.index("landing-hero-content")
        ]
        self.assertEqual(wall.count("<img"), 3 * 8 * 2)

    def test_gamer_does_not_get_the_landing(self):
        self.client.force_login(create_gamer("alex"))
        response = self.client.get(reverse("vault:index"))
        self.assertContains(response, "Welcome back")
        self.assertNotContains(response, "How it works")
