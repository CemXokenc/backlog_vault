from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F
from django.urls import reverse

from vault.validators import (
    validate_release_year,
    validate_rating,
    MIN_RATING,
    MAX_RATING,
)


class Gamer(AbstractUser):
    nickname = models.CharField(
        max_length=255,
        blank=True,
    )
    bio = models.TextField(
        blank=True,
    )
    favorite_genre = models.ForeignKey(
        "Genre",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fans",
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

    def get_absolute_url(self):
        return reverse("vault:game-detail", args=[self.pk])


class LibraryEntry(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        PLAYING = "playing", "Playing"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    gamer = models.ForeignKey(
        Gamer,
        on_delete=models.CASCADE,
        related_name="library_entries",
    )
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name="library_entries",
    )
    platform = models.ForeignKey(
        Platform,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="library_entries",
    )
    status = models.CharField(
        max_length=10,
        choices=Status,
        default=Status.PLANNED,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[validate_rating],
        null=True,
        blank=True,
    )
    hours_played = models.PositiveIntegerField(
        default=0,
    )
    started_at = models.DateField(
        null=True,
        blank=True,
    )
    finished_at = models.DateField(
        null=True,
        blank=True,
    )
    note = models.TextField(
        blank=True,
    )

    class Meta:
        verbose_name_plural = "library entries"
        ordering = ["-rating", "hours_played"]
        constraints = [
            models.UniqueConstraint(
                fields=["gamer", "game"],
                name="unique_gamer_game_entry",
            ),
            models.CheckConstraint(
                condition=Q(rating__isnull=True)
                | Q(rating__gte=MIN_RATING, rating__lte=MAX_RATING),
                name="rating_within_bounds",
            ),
            models.CheckConstraint(
                condition=Q(started_at__isnull=True)
                | Q(finished_at__isnull=True)
                | Q(finished_at__gte=F("started_at")),
                name="finished_not_before_started",
            ),
        ]

    def __str__(self):
        return f"{self.gamer} - {self.game} ({self.status})"


class Collection(models.Model):
    title = models.CharField(
        max_length=255,
    )
    description = models.TextField(
        blank=True,
    )
    owner = models.ForeignKey(
        Gamer,
        on_delete=models.CASCADE,
        related_name="collections",
    )
    games = models.ManyToManyField(
        Game,
        blank=True,
        related_name="collections",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("vault:collection-detail", args=[self.pk])
