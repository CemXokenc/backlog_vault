from django.core.management import call_command
from django.test import TestCase

from vault.models import (
    Collection,
    Comment,
    Developer,
    Game,
    Gamer,
    Genre,
    LibraryEntry,
    Platform,
)
from vault.roles import MODERATORS_GROUP


class SeedDataTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_data", verbosity=0)

    def test_demo_users_have_the_expected_roles(self):
        admin = Gamer.objects.get(username="demo_admin")
        moderator = Gamer.objects.get(username="demo_moderator")
        player = Gamer.objects.get(username="demo_user")
        self.assertTrue(admin.is_superuser and admin.is_staff)
        self.assertTrue(moderator.is_staff and not moderator.is_superuser)
        self.assertTrue(
            moderator.groups.filter(name=MODERATORS_GROUP).exists(),
        )
        self.assertTrue(moderator.has_perm("vault.add_game"))
        self.assertFalse(player.is_staff)
        self.assertFalse(player.has_perm("vault.add_game"))
        self.assertTrue(player.check_password("testpass123"))

    def test_demo_player_has_a_populated_profile(self):
        player = Gamer.objects.get(username="demo_user")
        self.assertEqual(
            LibraryEntry.objects.filter(gamer=player).count(),
            4,
        )
        self.assertTrue(Collection.objects.filter(owner=player).exists())

    def test_seed_is_idempotent(self):
        games = Game.objects.count()
        gamers = Gamer.objects.count()
        call_command("seed_data", verbosity=0)
        self.assertEqual(Game.objects.count(), games)
        self.assertEqual(Gamer.objects.count(), gamers)
        self.assertEqual(
            LibraryEntry.objects.filter(gamer__username="demo_user").count(),
            4,
        )

    def test_seed_creates_comments_without_duplicates(self):
        self.assertTrue(Comment.objects.filter(game__isnull=False).exists())
        self.assertTrue(
            Comment.objects.filter(collection__isnull=False).exists(),
        )
        comments = Comment.objects.count()
        call_command("seed_data", verbosity=0)
        self.assertEqual(Comment.objects.count(), comments)

    def test_seed_fills_a_big_catalog(self):
        self.assertGreaterEqual(Game.objects.count(), 60)
        self.assertGreaterEqual(Developer.objects.count(), 35)
        self.assertGreaterEqual(Genre.objects.count(), 15)
        self.assertGreaterEqual(Platform.objects.count(), 8)

    def test_every_reference_item_is_used_by_a_game(self):
        self.assertFalse(Developer.objects.filter(games__isnull=True).exists())
        self.assertFalse(Genre.objects.filter(games__isnull=True).exists())
        self.assertFalse(Platform.objects.filter(games__isnull=True).exists())

    def test_library_platform_belongs_to_the_game(self):
        entries = LibraryEntry.objects.filter(platform__isnull=False)
        for entry in entries.select_related("game", "platform"):
            with self.subTest(entry=str(entry)):
                self.assertTrue(
                    entry.game.platforms.filter(pk=entry.platform.pk).exists(),
                )
