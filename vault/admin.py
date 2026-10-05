from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import (
    AdminPasswordChangeForm,
    UserChangeForm,
    UserCreationForm,
)

from vault.models import (
    Collection,
    Developer,
    Game,
    Gamer,
    Genre,
    LibraryEntry,
    Platform,
)
from vault.roles import MODERATORS_GROUP, ensure_moderators_group

EXTRA_FIELDS = (
    "Additional info",
    {"fields": ("nickname", "bio", "favorite_genre")},
)

admin.site.unregister(Group)


class GamerAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Gamer


class GamerAdminChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Gamer


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(Gamer)
class GamerAdmin(UserAdmin, ModelAdmin):
    form = GamerAdminChangeForm
    add_form = GamerAdminCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = (
        "username",
        "nickname",
        "email",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    fieldsets = UserAdmin.fieldsets + (EXTRA_FIELDS,)
    add_fieldsets = UserAdmin.add_fieldsets + (EXTRA_FIELDS,)
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
class GenreAdmin(ModelAdmin):
    search_fields = ("name",)


@admin.register(Platform)
class PlatformAdmin(ModelAdmin):
    search_fields = ("name",)


@admin.register(Developer)
class DeveloperAdmin(ModelAdmin):
    list_display = ("name", "country")
    list_filter = ("country",)
    search_fields = ("name", "country")


@admin.register(Game)
class GameAdmin(ModelAdmin):
    list_display = ("title", "release_year", "developer")
    list_filter = ("genres", "platforms", "release_year")
    search_fields = ("title", "developer__name")
    filter_horizontal = ("genres", "platforms")


@admin.register(LibraryEntry)
class LibraryEntryAdmin(ModelAdmin):
    list_display = ("gamer", "game", "status", "rating", "hours_played")
    list_filter = ("status", "platform")
    search_fields = ("gamer__username", "game__title")


@admin.register(Collection)
class CollectionAdmin(ModelAdmin):
    list_display = ("title", "owner")
    search_fields = ("title", "owner__username")
    filter_horizontal = ("games",)
