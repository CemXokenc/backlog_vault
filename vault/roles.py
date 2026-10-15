from django.contrib.auth.models import Group, Permission

MODERATORS_GROUP = "Moderators"
MODERATED_MODELS = ("game", "genre", "platform", "developer", "comment")
PERMISSION_ACTIONS = ("add", "change", "delete", "view")

DEMO_USERS = {
    "admin": "demo_admin",
    "moderator": "demo_moderator",
    "user": "demo_user",
}


def ensure_moderators_group():
    """Create the Moderators group with catalog permissions (idempotent)."""
    group, _ = Group.objects.get_or_create(name=MODERATORS_GROUP)
    codenames = [
        f"{action}_{model}"
        for model in MODERATED_MODELS
        for action in PERMISSION_ACTIONS
    ]
    permissions = Permission.objects.filter(
        content_type__app_label="vault",
        codename__in=codenames,
    )
    group.permissions.set(permissions)
    return group
