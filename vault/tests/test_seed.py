from django.core.management import call_command
from django.test import TestCase

from vault.models import Collection, Game, Gamer, LibraryEntry
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
