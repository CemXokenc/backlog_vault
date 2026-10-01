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
