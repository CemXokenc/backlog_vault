from django.core.management.base import BaseCommand

from vault.roles import MODERATORS_GROUP, ensure_moderators_group


class Command(BaseCommand):
    help = "Create the Moderators group."  # noqa: VNE003

    def handle(self, *args, **options):
        group = ensure_moderators_group()
        self.stdout.write(
            self.style.SUCCESS(
                f"{MODERATORS_GROUP}: {group.permissions.count()} permissions",
            )
        )
