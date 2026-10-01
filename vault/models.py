from django.contrib.auth.models import AbstractUser
from django.db import models


class Gamer(AbstractUser):
    nickname = models.CharField(
        max_length=255,
        blank=True,
    )
    bio = models.TextField(
        blank=True,
    )

    def __str__(self):
        if self.nickname:
            return f"{self.username} ({self.nickname})"
        return self.username


class Genre(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Platform(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Developer(models.Model):
    name = models.CharField(
        max_length=255,
    )
    country = models.CharField(
        max_length=255,
    )

    class Meta:
        ordering = ["name", "country"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "country"],
                name="unique_developer_name_country",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.country})"
