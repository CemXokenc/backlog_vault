from django.test import TestCase
from django.urls import reverse

from vault.models import Gamer
from vault.roles import MODERATORS_GROUP
from vault.tests.helpers import (
    create_catalog,
    create_collection,
    create_entry,
    create_gamer,
)


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


class UnfoldAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = create_gamer("boss", is_staff=True, is_superuser=True)
        cls.catalog = create_catalog()
        cls.entry = create_entry(cls.admin, cls.catalog.game)
        cls.collection = create_collection(cls.admin, games=[cls.catalog.game])

    def setUp(self):
        self.client.force_login(self.admin)

    def test_every_admin_page_opens(self):
        objects = {
            "gamer": self.admin,
            "genre": self.catalog.genre,
            "platform": self.catalog.platform,
            "developer": self.catalog.developer,
            "game": self.catalog.game,
            "libraryentry": self.entry,
            "collection": self.collection,
        }
        urls = [reverse("admin:index"), reverse("admin:auth_group_changelist")]
        for model, obj in objects.items():
            urls.append(reverse(f"admin:vault_{model}_changelist"))
            urls.append(reverse(f"admin:vault_{model}_add"))
            urls.append(reverse(f"admin:vault_{model}_change", args=[obj.pk]))
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_admin_uses_the_unfold_theme(self):
        response = self.client.get(reverse("admin:index"))
        self.assertContains(response, "unfold")
        self.assertContains(response, "Backlog Vault")

    def test_admin_can_create_a_gamer_with_profile_fields(self):
        response = self.client.post(
            reverse("admin:vault_gamer_add"),
            {
                "username": "created_in_admin",
                "usable_password": "true",
                "password1": "Str0ng-pass-77",
                "password2": "Str0ng-pass-77",
                "nickname": "Admin Made",
                "bio": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        gamer = Gamer.objects.get(username="created_in_admin")
        self.assertEqual(gamer.nickname, "Admin Made")
        self.assertTrue(gamer.check_password("Str0ng-pass-77"))
