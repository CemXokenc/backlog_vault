from django.db.models import Count, F, Q
from django.shortcuts import render

from vault.models import (
    Collection,
    Developer,
    Game,
    Gamer,
    Genre,
    LibraryEntry,
    Platform,
)

COVER_WALL_ROWS = 3
COVER_WALL_ROW_SIZE = 8


def get_cover_wall():
    """Rows of game covers for the animated landing background.

    Every row is doubled so the CSS animation can loop without a jump.
    Returns an empty list when there are too few covers to look good.
    """
    wanted = COVER_WALL_ROWS * COVER_WALL_ROW_SIZE
    covered = Game.objects.exclude(cover="", cover_url="")
    covers = [game.cover_source for game in covered.order_by("?")[:wanted]]
    if len(covers) < 6:
        return []
    pool = (covers * -(-wanted // len(covers)))[:wanted]
    rows = [
        pool[start : start + COVER_WALL_ROW_SIZE]
        for start in range(0, wanted, COVER_WALL_ROW_SIZE)
    ]
    return [row + row for row in rows]


def landing(request):
    """Home page for guests: what the site is and a taste of the catalog."""
    featured_games = (
        Game.objects.with_stats()
        .select_related("developer")
        .prefetch_related("genres")
        .order_by(
            "-num_players",
            F("avg_rating").desc(nulls_last=True),
            "title",
        )[:6]
    )
    context = {
        "num_games": Game.objects.count(),
        "num_developers": Developer.objects.count(),
        "num_genres": Genre.objects.count(),
        "num_platforms": Platform.objects.count(),
        "cover_wall": get_cover_wall(),
        "featured_games": featured_games,
    }
    return render(request, "vault/home_guest.html", context=context)


def index(request):
    if not request.user.is_authenticated:
        return landing(request)

    context = {"num_games": Game.objects.count()}

    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    my_library = LibraryEntry.objects.filter(gamer=request.user).aggregate(
        total=Count("id"),
        playing=Count("id", filter=Q(status=LibraryEntry.Status.PLAYING)),
        completed=Count("id", filter=Q(status=LibraryEntry.Status.COMPLETED)),
    )

    context.update(
        {
            "num_visits": num_visits,
            "num_genres": Genre.objects.count(),
            "num_platforms": Platform.objects.count(),
            "num_developers": Developer.objects.count(),
            "num_collections": Collection.objects.count(),
            "num_gamers": Gamer.objects.count(),
            "my_library": my_library,
        },
    )

    return render(request, "vault/home.html", context=context)
