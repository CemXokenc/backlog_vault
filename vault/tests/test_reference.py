from django.test import TestCase
from django.urls import reverse

from vault.models import Developer, Genre, Platform
from vault.tests.helpers import create_catalog, create_moderator


class ReferencePagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gamer = create_moderator("mod")
        cls.catalog = create_catalog()

    def setUp(self):
        self.client.force_login(self.gamer)

    def test_lists_show_game_counts(self):
        for prefix, name in (
            ("genre", "Roguelike"),
            ("platform", "PC"),
            ("developer", "Supergiant"),
        ):
            with self.subTest(prefix=prefix):
                response = self.client.get(reverse(f"vault:{prefix}-list"))
                self.assertContains(response, name)
                item = response.context["object_list"][0]
                self.assertEqual(item.num_games, 1)

    def test_developer_list_shows_country_column(self):
        response = self.client.get(reverse("vault:developer-list"))
        self.assertContains(response, "Country")
        self.assertContains(response, "USA")
        genres = self.client.get(reverse("vault:genre-list"))
        self.assertNotContains(genres, "Country")

    def test_search_filters_by_name(self):
        Genre.objects.create(name="Puzzle")
        response = self.client.get(reverse("vault:genre-list") + "?query=puz")
        names = [item.name for item in response.context["object_list"]]
        self.assertEqual(names, ["Puzzle"])

    def test_create_update_delete_genre(self):
        response = self.client.post(
            reverse("vault:genre-create"),
            {"name": "Metroidvania"},
            follow=True,
        )
        self.assertContains(response, "Genre was successfully created!")
        genre = Genre.objects.get(name="Metroidvania")
        response = self.client.post(
            reverse("vault:genre-update", args=[genre.pk]),
            {"name": "Metroidvania!"},
            follow=True,
        )
        self.assertContains(response, "Genre was successfully updated!")
        response = self.client.post(
            reverse("vault:genre-delete", args=[genre.pk]),
            follow=True,
        )
        self.assertContains(response, "Genre was successfully deleted!")
        self.assertFalse(Genre.objects.filter(pk=genre.pk).exists())

    def test_platform_duplicate_name_is_rejected(self):
        response = self.client.post(
            reverse("vault:platform-create"),
            {"name": "PC"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Platform.objects.filter(name="PC").count(), 1)

    def test_developer_pair_must_be_unique(self):
        url = reverse("vault:developer-create")
        data = {"name": "Supergiant", "country": "USA"}
        self.assertEqual(self.client.post(url, data).status_code, 200)
        other_country = {"name": "Supergiant", "country": "Poland"}
        self.assertEqual(self.client.post(url, other_country).status_code, 302)
        self.assertEqual(
            Developer.objects.filter(name="Supergiant").count(), 2
        )

    def test_delete_pages_explain_the_consequences(self):
        pages = (
            ("genre", self.catalog.genre, "favorite"),
            ("platform", self.catalog.platform, "no platform"),
            ("developer", self.catalog.developer, "without a developer"),
        )
        for prefix, obj, hint in pages:
            with self.subTest(prefix=prefix):
                url = reverse(f"vault:{prefix}-delete", args=[obj.pk])
                response = self.client.get(url)
                self.assertContains(response, "1 game(s)")
                self.assertContains(response, hint)
