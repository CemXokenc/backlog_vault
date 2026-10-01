from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from vault.models import Gamer


@admin.register(Gamer)
class GamerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("nickname",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("nickname", "bio",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional info", {"fields": ("nickname", "bio",)}),
    )
