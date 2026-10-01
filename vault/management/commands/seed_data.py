from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from vault.models import (
    Collection,
    Developer,
    Game,
    Gamer,
    Genre,
    LibraryEntry,
    Platform,
)

DEMO_PASSWORD = "testpass123"

GENRES = ["RPG", "Action", "Adventure", "Puzzle", "Roguelike", "Platformer"]

PLATFORMS = ["PC", "PlayStation 5", "Xbox Series X", "Nintendo Switch"]

DEVELOPERS = [
    ("CD Projekt Red", "Poland"),
    ("FromSoftware", "Japan"),
    ("Valve", "USA"),
    ("Supergiant Games", "USA"),
    ("Nintendo", "Japan"),
]

PC = "PC"
PS5 = "PlayStation 5"
XBOX = "Xbox Series X"
SWITCH = "Nintendo Switch"

GAMES = [
    {
        "title": "The Witcher 3: Wild Hunt",
        "release_year": 2015,
        "developer": "CD Projekt Red",
        "genres": ["RPG", "Action"],
        "platforms": [PC, PS5, XBOX, SWITCH],
        "description": "Open-world RPG about a monster hunter.",
    },
    {
        "title": "Cyberpunk 2077",
        "release_year": 2020,
        "developer": "CD Projekt Red",
        "genres": ["RPG", "Action"],
        "platforms": [PC, PS5, XBOX],
        "description": "Sci-fi RPG set in Night City.",
    },
    {
        "title": "Elden Ring",
        "release_year": 2022,
        "developer": "FromSoftware",
        "genres": ["RPG", "Action", "Adventure"],
        "platforms": [PC, PS5, XBOX],
        "description": "Open-world action RPG in the Lands Between.",
    },
    {
        "title": "Dark Souls III",
        "release_year": 2016,
        "developer": "FromSoftware",
        "genres": ["RPG", "Action"],
        "platforms": [PC, PS5, XBOX],
        "description": "Punishing action RPG about linking the fire.",
    },
    {
        "title": "Sekiro: Shadows Die Twice",
        "release_year": 2019,
        "developer": "FromSoftware",
        "genres": ["Action", "Adventure"],
        "platforms": [PC, PS5, XBOX],
        "description": "Shinobi action game in feudal Japan.",
    },
    {
        "title": "Portal 2",
        "release_year": 2011,
        "developer": "Valve",
        "genres": ["Puzzle", "Adventure"],
        "platforms": [PC, SWITCH],
        "description": "Physics puzzles with portals and GLaDOS.",
    },
    {
        "title": "Half-Life 2",
        "release_year": 2004,
        "developer": "Valve",
        "genres": ["Action", "Adventure"],
        "platforms": [PC],
        "description": "Classic first-person shooter with a crowbar.",
    },
    {
        "title": "Half-Life: Alyx",
        "release_year": 2020,
        "developer": "Valve",
        "genres": ["Action", "Adventure"],
        "platforms": [PC],
        "description": "VR prequel in the Half-Life universe.",
    },
    {
        "title": "Hades",
        "release_year": 2020,
        "developer": "Supergiant Games",
        "genres": ["Roguelike", "Action"],
        "platforms": [PC, SWITCH, PS5, XBOX],
        "description": "Escape the Underworld, again and again.",
    },
    {
        "title": "The Legend of Zelda: Breath of the Wild",
        "release_year": 2017,
        "developer": "Nintendo",
        "genres": ["Adventure", "Action"],
        "platforms": [SWITCH],
        "description": "Explore Hyrule however you like.",
    },
    {
        "title": "Super Mario Odyssey",
        "release_year": 2017,
        "developer": "Nintendo",
        "genres": ["Platformer", "Adventure"],
        "platforms": [SWITCH],
        "description": "Mario travels the world with a living hat.",
    },
    {
        "title": "Metroid Dread",
        "release_year": 2021,
        "developer": "Nintendo",
        "genres": ["Platformer", "Action"],
        "platforms": [SWITCH],
        "description": "Samus is hunted by E.M.M.I. robots.",
    },
]

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


class Command(BaseCommand):
    help = "Fill the database with demo data."  # noqa: VNE003

    @transaction.atomic
    def handle(self, *args, **options):
        genres = self.create_genres()
        platforms = self.create_platforms()
        developers = self.create_developers()
        games = self.create_games(genres, platforms, developers)
        gamers = self.create_gamers(genres)
        self.create_entries(gamers, games, platforms)
        self.create_collections(gamers, games)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Demo users: alex, maria, taras "
                f"(password: {DEMO_PASSWORD})"
            )
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
                name=name, defaults={"country": country}
            )[0]
            for name, country in DEVELOPERS
        }

    @staticmethod
    def create_games(genres, platforms, developers):
        games = {}
        for spec in GAMES:
            game, _ = Game.objects.update_or_create(
                title=spec["title"],
                release_year=spec["release_year"],
                defaults={
                    "description": spec["description"],
                    "developer": developers[spec["developer"]],
                },
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
            gamers[gamer.username] = gamer
        return gamers

    @staticmethod
    def create_entries(gamers, games, platforms):
        for (
            username,
            title,
            status,
            rating,
            hours,
            started_at,
            finished_at,
            platform_name,
            note,
        ) in ENTRIES:
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
        for owner, title, description, game_titles in COLLECTIONS:
            collection, _ = Collection.objects.update_or_create(
                owner=gamers[owner],
                title=title,
                defaults={"description": description},
            )
            collection.games.set([games[name] for name in game_titles])
