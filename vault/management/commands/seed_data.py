from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from vault.management.commands._activity import (
    EXTRA_COLLECTION_COMMENTS,
    EXTRA_COLLECTIONS,
    EXTRA_ENTRIES,
    EXTRA_GAME_COMMENTS,
)
from vault.management.commands._catalog import (
    DEVELOPERS,
    GAMES,
    GENRES,
    PC,
    PLATFORMS,
    PS5,
    SWITCH,
    XBOX,
)
from vault.models import (
    Collection,
    Comment,
    Developer,
    Game,
    Gamer,
    Genre,
    LibraryEntry,
    Platform,
)
from vault.roles import ensure_moderators_group

DEMO_PASSWORD = "testpass123"

GAMERS = [
    {
        "username": "alex",
        "nickname": "Alex the Witcher",
        "bio": "Story-driven RPGs are my thing.",
        "favorite_genre": "RPG",
    },
    {
        "username": "maria",
        "nickname": "Masha",
        "bio": "Nintendo fan, roguelike addict.",
        "favorite_genre": "Roguelike",
    },
    {
        "username": "taras",
        "nickname": "Taras",
        "bio": "I like hard games and FromSoftware.",
        "favorite_genre": "Action",
    },
    {
        "username": "demo_admin",
        "nickname": "Demo Admin",
        "bio": "Superuser: can do everything, including the admin panel.",
        "favorite_genre": "RPG",
        "role": "admin",
    },
    {
        "username": "demo_moderator",
        "nickname": "Demo Moderator",
        "bio": "Moderator: manages games, genres, platforms, developers.",
        "favorite_genre": "Adventure",
        "role": "moderator",
    },
    {
        "username": "demo_user",
        "nickname": "Demo Player",
        "bio": "Regular player: library, ratings and collections.",
        "favorite_genre": "Roguelike",
    },
]

Status = LibraryEntry.Status

# username, game title, status, rating, hours,
# started_at, finished_at, platform, note
ENTRIES = [
    (
        "alex",
        "The Witcher 3: Wild Hunt",
        Status.COMPLETED,
        10,
        180,
        date(2025, 1, 10),
        date(2025, 3, 2),
        PC,
        "Best story ever.",
    ),
    (
        "alex",
        "Cyberpunk 2077",
        Status.COMPLETED,
        8,
        75,
        date(2024, 5, 1),
        date(2024, 6, 12),
        PC,
        "Great after patches.",
    ),
    (
        "alex",
        "Portal 2",
        Status.COMPLETED,
        9,
        9,
        date(2023, 11, 3),
        date(2023, 11, 5),
        PC,
        "",
    ),
    (
        "alex",
        "Elden Ring",
        Status.PLAYING,
        None,
        64,
        date(2026, 8, 15),
        None,
        PC,
        "Stuck on Malenia.",
    ),
    (
        "alex",
        "Dark Souls III",
        Status.DROPPED,
        4,
        12,
        date(2025, 9, 1),
        None,
        PC,
        "Too hard for me.",
    ),
    ("alex", "Hades", Status.PLANNED, None, 0, None, None, None, ""),
    (
        "alex",
        "Sekiro: Shadows Die Twice",
        Status.PLANNED,
        None,
        0,
        None,
        None,
        None,
        "",
    ),
    (
        "maria",
        "Hades",
        Status.COMPLETED,
        10,
        55,
        date(2025, 2, 1),
        date(2025, 3, 10),
        SWITCH,
        "Just one more run.",
    ),
    (
        "maria",
        "The Legend of Zelda: Breath of the Wild",
        Status.COMPLETED,
        10,
        120,
        date(2024, 1, 5),
        date(2024, 4, 20),
        SWITCH,
        "",
    ),
    (
        "maria",
        "Super Mario Odyssey",
        Status.COMPLETED,
        9,
        30,
        date(2024, 6, 1),
        date(2024, 6, 25),
        SWITCH,
        "",
    ),
    (
        "maria",
        "Portal 2",
        Status.COMPLETED,
        9,
        8,
        date(2025, 5, 2),
        date(2025, 5, 3),
        SWITCH,
        "",
    ),
    (
        "maria",
        "Metroid Dread",
        Status.PLAYING,
        None,
        25,
        date(2026, 9, 10),
        None,
        SWITCH,
        "",
    ),
    (
        "maria",
        "Half-Life 2",
        Status.DROPPED,
        5,
        3,
        date(2024, 10, 1),
        None,
        PC,
        "Not my style.",
    ),
    ("maria", "Elden Ring", Status.PLANNED, None, 0, None, None, None, ""),
    (
        "taras",
        "Sekiro: Shadows Die Twice",
        Status.COMPLETED,
        9,
        45,
        date(2025, 4, 1),
        date(2025, 5, 15),
        PC,
        "",
    ),
    (
        "taras",
        "Elden Ring",
        Status.COMPLETED,
        10,
        110,
        date(2024, 3, 1),
        date(2024, 5, 30),
        PS5,
        "Masterpiece.",
    ),
    (
        "taras",
        "Dark Souls III",
        Status.COMPLETED,
        9,
        70,
        date(2023, 7, 1),
        date(2023, 8, 20),
        PS5,
        "",
    ),
    (
        "taras",
        "Half-Life: Alyx",
        Status.COMPLETED,
        9,
        15,
        date(2025, 7, 1),
        date(2025, 7, 12),
        PC,
        "",
    ),
    (
        "taras",
        "Half-Life 2",
        Status.COMPLETED,
        10,
        14,
        date(2025, 6, 1),
        date(2025, 6, 8),
        PC,
        "",
    ),
    (
        "taras",
        "The Witcher 3: Wild Hunt",
        Status.PLAYING,
        None,
        40,
        date(2026, 8, 1),
        None,
        PS5,
        "",
    ),
    (
        "taras",
        "Cyberpunk 2077",
        Status.DROPPED,
        6,
        8,
        date(2024, 2, 1),
        None,
        PC,
        "Bugs at launch.",
    ),
    ("taras", "Metroid Dread", Status.PLANNED, None, 0, None, None, None, ""),
]

# owner, title, description, game titles
COLLECTIONS = [
    (
        "alex",
        "Best RPGs",
        "Stories worth getting lost in.",
        ["The Witcher 3: Wild Hunt", "Cyberpunk 2077", "Elden Ring"],
    ),
    (
        "alex",
        "Play before the end of the year",
        "Backlog goals.",
        ["Hades", "Sekiro: Shadows Die Twice"],
    ),
    (
        "maria",
        "Cozy Switch evenings",
        "Relaxing games for the sofa.",
        [
            "Super Mario Odyssey",
            "The Legend of Zelda: Breath of the Wild",
            "Portal 2",
        ],
    ),
    (
        "taras",
        "Souls-like challenge",
        "Prepare to die.",
        ["Elden Ring", "Dark Souls III", "Sekiro: Shadows Die Twice"],
    ),
    (
        "taras",
        "Valve classics",
        "Everything with a crowbar and portals.",
        ["Half-Life 2", "Half-Life: Alyx", "Portal 2"],
    ),
]

ENTRIES += [
    (
        "demo_user",
        "Hades",
        Status.COMPLETED,
        9,
        40,
        date(2026, 1, 5),
        date(2026, 2, 1),
        PC,
        "A great one to demo.",
    ),
    (
        "demo_user",
        "Portal 2",
        Status.COMPLETED,
        10,
        9,
        date(2026, 3, 2),
        date(2026, 3, 3),
        PC,
        "",
    ),
    (
        "demo_user",
        "Elden Ring",
        Status.PLAYING,
        None,
        20,
        date(2026, 8, 1),
        None,
        PC,
        "",
    ),
    (
        "demo_user",
        "Metroid Dread",
        Status.PLANNED,
        None,
        0,
        None,
        None,
        None,
        "",
    ),
]

COLLECTIONS += [
    ("demo_user", "My favourites", "Demo collection.", ["Hades", "Portal 2"]),
]

GAME_COMMENTS = [
    ("maria", "Hades", "Best roguelike I have played, great story."),
    ("alex", "Elden Ring", "Took me 120 hours and I want to start over."),
    ("taras", "Portal 2", "The co-op campaign is as good as the main one."),
]

COLLECTION_COMMENTS = [
    ("maria", "Best RPGs", "Nice list! I would add Disco Elysium."),
    ("taras", "My favourites", "Great taste, Portal 2 is a classic."),
]


class Command(BaseCommand):
    help = "Fill the database with demo data."  # noqa: VNE003

    @transaction.atomic
    def handle(self, *args, **options):
        ensure_moderators_group()
        genres = self.create_genres()
        platforms = self.create_platforms()
        developers = self.create_developers()
        games = self.create_games(genres, platforms, developers)
        gamers = self.create_gamers(genres)
        self.create_entries(gamers, games, platforms)
        self.create_collections(gamers, games)
        self.create_comments(gamers, games)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Demo logins (password: {DEMO_PASSWORD}): "
                "demo_admin, demo_moderator, demo_user, alex, maria, taras",
            ),
        )

    @staticmethod
    def create_genres():
        return {
            name: Genre.objects.get_or_create(name=name)[0] for name in GENRES
        }

    @staticmethod
    def create_platforms():
        return {
            name: Platform.objects.get_or_create(name=name)[0]
            for name in PLATFORMS
        }

    @staticmethod
    def create_developers():
        return {
            name: Developer.objects.get_or_create(
                name=name,
                defaults={"country": country},
            )[0]
            for name, country in DEVELOPERS
        }

    @staticmethod
    def create_games(genres, platforms, developers):
        games = {}
        for spec in GAMES:
            defaults = {
                "description": spec["description"],
                "developer": developers[spec["developer"]],
            }
            if spec["cover_url"]:
                defaults["cover_url"] = spec["cover_url"]
            game, _ = Game.objects.update_or_create(
                title=spec["title"],
                release_year=spec["release_year"],
                defaults=defaults,
            )
            game.genres.set([genres[name] for name in spec["genres"]])
            game.platforms.set([platforms[name] for name in spec["platforms"]])
            games[game.title] = game
        return games

    @staticmethod
    def create_gamers(genres):
        gamers = {}
        for spec in GAMERS:
            gamer, created = Gamer.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "nickname": spec["nickname"],
                    "bio": spec["bio"],
                    "favorite_genre": genres[spec["favorite_genre"]],
                },
            )
            if created:
                gamer.set_password(DEMO_PASSWORD)
                gamer.save()
            Command.apply_role(gamer, spec.get("role"))
            gamers[gamer.username] = gamer
        return gamers

    @staticmethod
    def create_entries(gamers, games, platforms):
        for entry in ENTRIES + EXTRA_ENTRIES:
            if len(entry) == 7:
                username, title, status, rating, hours, platform_name, note = (
                    entry
                )
                started_at = finished_at = None
            else:
                (
                    username,
                    title,
                    status,
                    rating,
                    hours,
                    started_at,
                    finished_at,
                    platform_name,
                    note,
                ) = entry
            LibraryEntry.objects.update_or_create(
                gamer=gamers[username],
                game=games[title],
                defaults={
                    "status": status,
                    "rating": rating,
                    "hours_played": hours,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "platform": platforms.get(platform_name),
                    "note": note,
                },
            )

    @staticmethod
    def create_collections(gamers, games):
        for owner, title, description, game_titles in (
            COLLECTIONS + EXTRA_COLLECTIONS
        ):
            collection, _ = Collection.objects.update_or_create(
                owner=gamers[owner],
                title=title,
                defaults={"description": description},
            )
            collection.games.set([games[name] for name in game_titles])

    @staticmethod
    def create_comments(gamers, games):
        for author, title, text in GAME_COMMENTS + EXTRA_GAME_COMMENTS:
            Comment.objects.get_or_create(
                author=gamers[author],
                game=games[title],
                text=text,
            )
        for author, title, text in (
            COLLECTION_COMMENTS + EXTRA_COLLECTION_COMMENTS
        ):
            Comment.objects.get_or_create(
                author=gamers[author],
                collection=Collection.objects.get(title=title),
                text=text,
            )

    @staticmethod
    def apply_role(gamer, role):
        if role == "admin":
            gamer.is_staff = True
            gamer.is_superuser = True
            gamer.save(update_fields=["is_staff", "is_superuser"])
        elif role == "moderator":
            gamer.is_staff = True
            gamer.save(update_fields=["is_staff"])
            gamer.groups.add(ensure_moderators_group())
