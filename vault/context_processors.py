from django.conf import settings

DEMO_ROLES = [
    ("admin", "Admin", "shield-lock"),
    ("moderator", "Moderator", "person-gear"),
    ("user", "Regular user", "person"),
]


def demo_mode(request):
    return {"demo_mode": settings.DEMO_MODE, "demo_roles": DEMO_ROLES}
