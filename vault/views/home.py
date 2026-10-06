from django.db.models import Count, Q
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


def index(request):
    context = {"num_games": Game.objects.count()}
    if not request.user.is_authenticated:
        return render(request, "vault/home.html", context=context)

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
