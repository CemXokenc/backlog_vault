from types import SimpleNamespace

from vault.roles import ensure_moderators_group
from vault.models import (
    Collection,
    Developer,
    Game,
    Gamer,
    Genre,
    LibraryEntry,
    Platform,
)

PASSWORD = "testpass123"


def create_gamer(username="alex", **extra):
    return Gamer.objects.create_user(
        username=username,
        password=PASSWORD,
        **extra,
    )


def create_moderator(username="moderator", **extra):
    gamer = create_gamer(username, is_staff=True, **extra)
    gamer.groups.add(ensure_moderators_group())
    return gamer


def create_catalog():
    genre = Genre.objects.create(name="Roguelike")
    platform = Platform.objects.create(name="PC")
    developer = Developer.objects.create(name="Supergiant", country="USA")
    game = Game.objects.create(
        title="Hades",
        release_year=2020,
        developer=developer,
    )
    game.genres.add(genre)
    game.platforms.add(platform)
    return SimpleNamespace(
        genre=genre,
        platform=platform,
        developer=developer,
        game=game,
    )


def create_entry(gamer, game, **extra):
    return LibraryEntry.objects.create(gamer=gamer, game=game, **extra)


def create_collection(owner, title="Favorites", games=()):
    collection = Collection.objects.create(owner=owner, title=title)
    collection.games.add(*games)
    return collection
