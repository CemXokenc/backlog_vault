from django.urls import path

from vault.views import (
    index,
    RegisterView,
    GenreListView,
    GenreCreateView,
    GenreUpdateView,
    GenreDeleteView,
    PlatformListView,
    PlatformCreateView,
    PlatformUpdateView,
    PlatformDeleteView,
    DeveloperListView,
    DeveloperCreateView,
    DeveloperUpdateView,
    DeveloperDeleteView,
    GameListView,
    GameDetailView,
    GameCreateView,
    GameUpdateView,
    GameDeleteView,
)

urlpatterns = [
    path("", index, name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("genres/create/", GenreCreateView.as_view(), name="genre-create"),
    path(
        "genres/<int:pk>/update/",
        GenreUpdateView.as_view(),
        name="genre-update",
    ),
    path(
        "genres/<int:pk>/delete/",
        GenreDeleteView.as_view(),
        name="genre-delete",
    ),
    path("platforms/", PlatformListView.as_view(), name="platform-list"),
    path(
        "platforms/create/",
        PlatformCreateView.as_view(),
        name="platform-create",
    ),
    path(
        "platforms/<int:pk>/update/",
        PlatformUpdateView.as_view(),
        name="platform-update",
    ),
    path(
        "platforms/<int:pk>/delete/",
        PlatformDeleteView.as_view(),
        name="platform-delete",
    ),
    path("developers/", DeveloperListView.as_view(), name="developer-list"),
    path(
        "developers/create/",
        DeveloperCreateView.as_view(),
        name="developer-create",
    ),
    path(
        "developers/<int:pk>/update/",
        DeveloperUpdateView.as_view(),
        name="developer-update",
    ),
    path(
        "developers/<int:pk>/delete/",
        DeveloperDeleteView.as_view(),
        name="developer-delete",
    ),
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path(
        "games/create/",
        GameCreateView.as_view(),
        name="game-create",
    ),
    path(
        "games/<int:pk>/update/",
        GameUpdateView.as_view(),
        name="game-update",
    ),
    path(
        "games/<int:pk>/delete/",
        GameDeleteView.as_view(),
        name="game-delete",
    ),
]

app_name = "vault"
