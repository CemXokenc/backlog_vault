from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from vault.models import Gamer, Genre


@admin.register(Gamer)
class GamerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("nickname",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("nickname", "bio",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional info", {"fields": ("nickname", "bio",)}),
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass
