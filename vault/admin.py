from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from vault.models import Gamer, Genre, Platform, Developer, Game, LibraryEntry

EXTRA_FIELDS = (
    "Additional info",
    {"fields": ("nickname", "bio", "favorite_genre")},
)


@admin.register(Gamer)
class GamerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("nickname",)
    fieldsets = UserAdmin.fieldsets + (EXTRA_FIELDS,)
    add_fieldsets = UserAdmin.add_fieldsets + (EXTRA_FIELDS,)


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
