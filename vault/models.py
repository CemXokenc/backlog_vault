from django.contrib.auth.models import AbstractUser
from django.db import models

from vault.validators import validate_release_year


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


class Game(models.Model):
    title = models.CharField(
        max_length=255,
    )
    release_year = models.PositiveSmallIntegerField(
        validators=[validate_release_year],
    )
    description = models.TextField(
        blank=True,
    )
    cover_url = models.URLField(
        blank=True,
    )
    developer = models.ForeignKey(
        Developer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="games",
    )
    genres = models.ManyToManyField(
        Genre,
        related_name="games",
    )
    platforms = models.ManyToManyField(
        Platform,
        related_name="games",
    )

    class Meta:
        ordering = ["-release_year", "title"]

    def __str__(self):
        return f"{self.title} ({self.release_year})"
