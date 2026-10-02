from django.urls import path

from vault.views import (
    index,
    RegisterView,
    GenreListView,
    GenreCreateView,
    GenreUpdateView,
    GenreDeleteView,
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
]

app_name = "vault"
