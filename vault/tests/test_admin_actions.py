from django.test import TestCase
from django.urls import reverse

from vault.roles import MODERATORS_GROUP
from vault.tests.helpers import create_gamer


class GamerAdminActionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_gamer("boss", is_staff=True, is_superuser=True)
        cls.newbie = create_gamer("newbie", is_active=False)
        cls.player = create_gamer("player")

    def setUp(self):
        self.client.force_login(self.admin)

    def run_action(self, action, *gamers):
        return self.client.post(
            reverse("admin:vault_gamer_changelist"),
            {
                "action": action,
                "_selected_action": [gamer.pk for gamer in gamers],
            },
            follow=True,
        )

    def test_activate_gamers(self):
        response = self.run_action("activate_gamers", self.newbie)
        self.assertContains(response, "1 gamer(s) activated.")
        self.newbie.refresh_from_db()
        self.assertTrue(self.newbie.is_active)

    def test_make_moderators_sets_staff_flag_and_group(self):
        self.run_action("make_moderators", self.player)
        self.player.refresh_from_db()
        self.assertTrue(self.player.is_staff)
        self.assertTrue(
            self.player.groups.filter(name=MODERATORS_GROUP).exists(),
        )
        self.assertTrue(self.player.has_perm("vault.add_game"))

    def test_remove_moderators_reverts_it(self):
        self.run_action("make_moderators", self.player)
        self.run_action("remove_moderators", self.player)
        player = type(self.player).objects.get(pk=self.player.pk)
        self.assertFalse(player.is_staff)
        self.assertFalse(player.groups.exists())
        self.assertFalse(player.has_perm("vault.add_game"))

    def test_superusers_are_not_demoted(self):
        self.run_action("remove_moderators", self.admin)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)

    def test_moderator_can_open_admin_but_only_sees_catalog(self):
        self.run_action("make_moderators", self.player)
        self.client.force_login(self.player)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Games")
        self.assertContains(response, "Genres")
        self.assertNotContains(response, "Library entries")
        self.assertNotContains(response, "Groups")

    def test_regular_player_cannot_open_admin(self):
        self.client.force_login(self.player)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response["Location"])
