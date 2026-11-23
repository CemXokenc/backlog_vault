from django.test import TestCase
from django.urls import reverse

from vault.tests.helpers import create_catalog, create_moderator

COVER = "https://example.com/cover.jpg"


class GameFormLayoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.game = create_catalog().game
        cls.game.cover_url = COVER
        cls.game.save()

    def setUp(self):
        self.client.force_login(create_moderator("mod"))

    def test_cover_preview_sits_next_to_the_main_fields(self):
        url = reverse("vault:game-update", args=[self.game.pk])
        html = self.client.get(url).content.decode()
        position = html.index('id="cover-preview"')
        for field in ("id_title", "id_release_year", "id_developer"):
            with self.subTest(field=field):
                self.assertLess(html.index(f'id="{field}"'), position)
        self.assertLess(position, html.index('id="id_genres_0"'))
        self.assertLess(position, html.index('id="id_description"'))

    def test_edit_form_previews_the_current_cover(self):
        url = reverse("vault:game-update", args=[self.game.pk])
        self.assertContains(self.client.get(url), f'data-initial="{COVER}"')

    def test_add_form_has_an_empty_preview(self):
        response = self.client.get(reverse("vault:game-create"))
        self.assertContains(response, 'id="cover-preview"')
        self.assertContains(response, 'data-initial=""')


class GameDetailHeroTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.game = create_catalog().game

    def test_hero_has_blurred_cover_when_game_has_one(self):
        self.game.cover_url = COVER
        self.game.save()
        response = self.client.get(self.game.get_absolute_url())
        self.assertContains(response, 'class="game-hero-bg"')

    def test_hero_works_without_a_cover(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertContains(response, "game-hero")
        self.assertNotContains(response, 'class="game-hero-bg"')
