from io import StringIO

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase

from vault.roles import MODERATORS_GROUP, ensure_moderators_group


class ModeratorsGroupTests(TestCase):
    def codenames(self):
        group = Group.objects.get(name=MODERATORS_GROUP)
        return set(group.permissions.values_list("codename", flat=True))

    def test_group_gets_catalog_permissions_only(self):
        ensure_moderators_group()
        codenames = self.codenames()
        self.assertEqual(len(codenames), 16)
        for model in ("game", "genre", "platform", "developer"):
            for action in ("add", "change", "delete", "view"):
                self.assertIn(f"{action}_{model}", codenames)
        for private in ("libraryentry", "collection", "gamer"):
            self.assertFalse(
                [name for name in codenames if name.endswith(private)],
            )

    def test_setup_is_idempotent(self):
        ensure_moderators_group()
        ensure_moderators_group()
        self.assertEqual(
            Group.objects.filter(name=MODERATORS_GROUP).count(), 1
        )
        self.assertEqual(len(self.codenames()), 16)

    def test_management_command(self):
        out = StringIO()
        call_command("setup_roles", stdout=out)
        self.assertIn("16 permissions", out.getvalue())
