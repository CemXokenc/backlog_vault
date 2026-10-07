from django.test import TestCase

from vault.models import Game
from vault.tests.helpers import create_catalog, create_entry, create_gamer


class GameStatsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.catalog = create_catalog()
        cls.game = cls.catalog.game
        cls.first = create_gamer("first")
        cls.second = create_gamer("second")
        cls.third = create_gamer("third")

    def test_with_stats_averages_ratings_and_counts_players(self):
        create_entry(self.first, self.game, status="completed", rating=8)
        create_entry(self.second, self.game, status="completed", rating=10)
        create_entry(self.third, self.game, status="planned")
        game = Game.objects.with_stats().get(pk=self.game.pk)
        self.assertEqual(game.avg_rating, 9)
        self.assertEqual(game.num_players, 3)

    def test_with_stats_for_game_without_entries(self):
        game = Game.objects.with_stats().get(pk=self.game.pk)
        self.assertIsNone(game.avg_rating)
        self.assertEqual(game.num_players, 0)

    def test_with_stats_is_available_on_related_managers(self):
        create_entry(self.first, self.game, status="completed", rating=6)
        genre_games = self.catalog.genre.games.with_stats()
        self.assertEqual(genre_games.get().avg_rating, 6)
