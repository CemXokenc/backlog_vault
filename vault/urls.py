from django.urls import path

from vault.views import index, RegisterView, GenreListView

urlpatterns = [
    path("", index, name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
]

app_name = "vault"
