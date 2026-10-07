from django.db.models import Avg, Count, F, Q
from django.shortcuts import render

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


DASHBOARD_CARDS = 4
SUGGESTIONS = 6
LATEST_COMMENTS = 5


def get_suggestions(user):
    """Popular games the gamer has not added yet, favorite genre first.

    Returns the games and how many of them match the favorite genre.
    """
    candidates = (
        Game.objects.with_stats()
        .select_related("developer")
        .prefetch_related("genres")
        .exclude(library_entries__gamer=user)
        .order_by(
            "-num_players",
            F("avg_rating").desc(nulls_last=True),
            "title",
        )
    )
    suggestions = []
    if user.favorite_genre_id:
        favorite_ids = Game.objects.filter(
            genres=user.favorite_genre_id,
        ).values("pk")
        favorites = candidates.filter(pk__in=favorite_ids)
        suggestions = list(favorites[:SUGGESTIONS])
    favorite_count = len(suggestions)
    if favorite_count < SUGGESTIONS:
        taken = [game.pk for game in suggestions]
        rest = candidates.exclude(pk__in=taken)[: SUGGESTIONS - favorite_count]
        suggestions += list(rest)
    return suggestions, favorite_count


def dashboard(request):
    """Home page of a signed-in gamer."""
    user = request.user
    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    entries = LibraryEntry.objects.filter(gamer=user).select_related("game")
    my_library = entries.aggregate(
        total=Count("id"),
        playing=Count("id", filter=Q(status=LibraryEntry.Status.PLAYING)),
        completed=Count("id", filter=Q(status=LibraryEntry.Status.COMPLETED)),
        avg_rating=Avg("rating"),
    )
    playing = entries.filter(status=LibraryEntry.Status.PLAYING)
    planned = entries.filter(status=LibraryEntry.Status.PLANNED)
    suggestions, favorite_count = get_suggestions(user)

    context = {
        "num_visits": num_visits,
        "num_games": Game.objects.count(),
        "num_genres": Genre.objects.count(),
        "num_platforms": Platform.objects.count(),
        "num_developers": Developer.objects.count(),
        "num_collections": Collection.objects.count(),
        "num_gamers": Gamer.objects.count(),
        "my_library": my_library,
        "cover_wall": get_cover_wall(),
        "playing_entries": playing.order_by("-pk")[:DASHBOARD_CARDS],
        "planned_entries": planned.order_by("-pk")[:DASHBOARD_CARDS],
        "suggestions": suggestions,
        "suggestions_by_genre": favorite_count > 0,
        "latest_comments": Comment.objects.select_related(
            "author",
            "game",
            "collection",
        )[:LATEST_COMMENTS],
    }
    return render(request, "vault/home.html", context=context)


def index(request):
    if request.user.is_authenticated:
        return dashboard(request)
    return landing(request)
