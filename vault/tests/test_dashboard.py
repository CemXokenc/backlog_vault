from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from vault.models import Comment, Game, Genre, LibraryEntry
from vault.tests.helpers import create_collection, create_entry, create_gamer

URL = "https://example.com/avatar.png"


def make_game(title, genre=None, **extra):
    game = Game.objects.create(title=title, release_year=2020, **extra)
    if genre:
        game.genres.add(genre)
    return game


class DashboardTests(TestCase):
    def setUp(self):
        self.rpg = Genre.objects.create(name="RPG")
        self.gamer = create_gamer("alex", favorite_genre=self.rpg)
        self.client.force_login(self.gamer)

    def get(self):
        return self.client.get(reverse("vault:index"))

    def test_greets_the_gamer_with_a_hero_and_counters(self):
        response = self.get()
        self.assertContains(response, "Welcome back, alex!")
        self.assertContains(response, "Visit #1")
        self.assertContains(response, "In your library")
        self.assertEqual(self.get().context["num_visits"], 2)

    def test_hero_shows_the_avatar(self):
        self.gamer.avatar_url = URL
        self.gamer.save()
        self.assertContains(self.get(), URL)

    def test_stats_reflect_the_library(self):
        game = make_game("A")
        other = make_game("B")
        create_entry(self.gamer, game, status="playing", rating=8)
        create_entry(self.gamer, other, status="completed", rating=6)
        library = self.get().context["my_library"]
        self.assertEqual(library["total"], 2)
        self.assertEqual(library["playing"], 1)
        self.assertEqual(library["completed"], 1)
        self.assertEqual(library["avg_rating"], 7)

    def test_shows_playing_and_planned_games(self):
        create_entry(self.gamer, make_game("Now"), status="playing")
        create_entry(self.gamer, make_game("Later"), status="planned")
        create_entry(self.gamer, make_game("Done"), status="completed")
        response = self.get()
        self.assertContains(response, "Continue playing")
        self.assertContains(response, "Up next in your backlog")
        self.assertContains(response, "Now")
        self.assertContains(response, "Later")
        self.assertNotContains(response, "Done")

    def test_empty_library_shows_a_call_to_action(self):
        response = self.get()
        self.assertContains(response, "Your backlog is empty")
        self.assertNotContains(response, "Continue playing")

    def test_suggestions_skip_games_already_in_the_library(self):
        owned = make_game("Owned", self.rpg)
        make_game("Fresh", self.rpg)
        create_entry(self.gamer, owned)
        titles = [game.title for game in self.get().context["suggestions"]]
        self.assertIn("Fresh", titles)
        self.assertNotIn("Owned", titles)

    def test_suggestions_start_with_the_favorite_genre(self):
        other = Genre.objects.create(name="Racing")
        popular = make_game("Popular racer", other)
        make_game("Quiet RPG", self.rpg)
        other_gamer = create_gamer("fan")
        create_entry(other_gamer, popular)
        context = self.get().context
        titles = [game.title for game in context["suggestions"]]
        self.assertEqual(titles, ["Quiet RPG", "Popular racer"])
        self.assertTrue(context["suggestions_by_genre"])
        self.assertContains(self.get(), "Starting with RPG games")

    def test_suggestions_without_favorite_genre_use_popularity(self):
        self.gamer.favorite_genre = None
        self.gamer.save()
        make_game("Anything")
        context = self.get().context
        self.assertEqual(len(context["suggestions"]), 1)
        self.assertFalse(context["suggestions_by_genre"])

    def test_latest_comments_feed_links_to_the_target(self):
        game = make_game("Talked about")
        Comment.objects.create(
            author=create_gamer("zed"),
            game=game,
            text="Great stuff",
        )
        collection = create_collection(self.gamer, "My list")
        Comment.objects.create(
            author=self.gamer,
            collection=collection,
            text="Mine too",
        )
        response = self.get()
        self.assertContains(response, "Latest comments")
        self.assertContains(response, "Great stuff")
        self.assertContains(response, "Mine too")
        self.assertContains(response, game.get_absolute_url())

    def test_query_count_does_not_grow_with_the_data(self):
        self.get()  # warm up the session
        for number in range(4):
            game = make_game(f"Game {number}", self.rpg)
            create_entry(self.gamer, game, status="playing")
        with CaptureQueriesContext(connection) as before:
            self.get()
        for number in range(4, 16):
            game = make_game(f"Game {number}", self.rpg)
            create_entry(self.gamer, game, status="planned")
            Comment.objects.create(
                author=self.gamer,
                game=game,
                text="Hello",
            )
        with CaptureQueriesContext(connection) as after:
            self.get()
        self.assertEqual(len(after), len(before))

    def test_library_status_links_use_real_status_values(self):
        values = {value for value, _ in LibraryEntry.Status.choices}
        self.assertTrue({"playing", "planned"} <= values)
