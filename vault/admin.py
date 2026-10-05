from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from vault.roles import MODERATORS_GROUP, ensure_moderators_group
from vault.models import (
    Gamer,
    Genre,
    Platform,
    Developer,
    Game,
    LibraryEntry,
    Collection,
)

EXTRA_FIELDS = (
    "Additional info",
    {"fields": ("nickname", "bio", "favorite_genre")},
)


@admin.register(Gamer)
class GamerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("nickname",)
    fieldsets = UserAdmin.fieldsets + (EXTRA_FIELDS,)
    add_fieldsets = UserAdmin.add_fieldsets + (EXTRA_FIELDS,)
    list_filter = UserAdmin.list_filter + ("groups",)
    actions = ["activate_gamers", "make_moderators", "remove_moderators"]

    @admin.action(description="Activate selected gamers")
    def activate_gamers(self, request, queryset):
        updated = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(
            request,
            f"{updated} gamer(s) activated.",
            messages.SUCCESS,
        )

    @admin.action(description="Make selected gamers moderators")
    def make_moderators(self, request, queryset):
        group = ensure_moderators_group()
        gamers = queryset.filter(is_superuser=False)
        for gamer in gamers:
            gamer.is_staff = True
            gamer.save(update_fields=["is_staff"])
            gamer.groups.add(group)
        self.message_user(
            request,
            f"{gamers.count()} gamer(s) are now in {MODERATORS_GROUP}.",
            messages.SUCCESS,
        )

    @admin.action(description="Remove moderator role from selected gamers")
    def remove_moderators(self, request, queryset):
        group = ensure_moderators_group()
        gamers = queryset.filter(is_superuser=False)
        for gamer in gamers:
            gamer.is_staff = False
            gamer.save(update_fields=["is_staff"])
            gamer.groups.remove(group)
        self.message_user(
            request,
            f"{gamers.count()} gamer(s) are no longer moderators.",
            messages.SUCCESS,
        )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    pass


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    filter_horizontal = ("genres", "platforms")


@admin.register(LibraryEntry)
class LibraryEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    filter_horizontal = ("games",)
