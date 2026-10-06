from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import generic

from vault.forms import (
    GameFilterForm,
    GameForm,
    CommentForm,
)
from vault.mixins import (
    ModelPermissionMixin,
    SearchMixin,
)
from vault.models import (
    Collection,
    Game,
    LibraryEntry,
)


class GameListView(
    SearchMixin,
    generic.ListView,
):
    template_name = "vault/games/list.html"
    queryset = (
        Game.objects.select_related("developer")
        .prefetch_related("genres")
        .with_stats()
        .order_by("-release_year", "title")
    )
    form_class = GameFilterForm
    search_field = "title"
    paginate_by = 12
    search_placeholder = "Search games"

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.form_class(self.request.GET)
        if form.is_valid():
            if form.cleaned_data["genre"]:
                queryset = queryset.filter(genres=form.cleaned_data["genre"])
            if form.cleaned_data["platform"]:
                queryset = queryset.filter(
                    platforms=form.cleaned_data["platform"],
                )

        return queryset


class GameDetailView(
    generic.DetailView,
):
    template_name = "vault/games/detail.html"
    queryset = (
        Game.objects.select_related("developer")
        .prefetch_related("genres", "platforms")
        .with_stats()
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["entries"] = LibraryEntry.objects.filter(
            game=self.object,
        ).select_related("gamer", "platform")
        context["comments"] = self.object.comments.select_related("author")
        if not user.is_authenticated:
            return context

        context["comment_form"] = CommentForm()
        context["my_entry"] = LibraryEntry.objects.filter(
            gamer=user,
            game=self.object,
        ).first()
        context["game_collections"] = self.object.collections.select_related(
            "owner",
        )
        my_collections = Collection.objects.filter(owner=user)
        context["addable_collections"] = my_collections.exclude(
            games=self.object,
        )
        context["removable_collections"] = my_collections.filter(
            games=self.object,
        )

        return context


class GameCreateView(
    ModelPermissionMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    permission_action = "add"
    template_name = "vault/games/form.html"
    model = Game
    form_class = GameForm
    success_message = "Game was successfully created!"


class GameUpdateView(
    ModelPermissionMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    permission_action = "change"
    template_name = "vault/games/form.html"
    model = Game
    form_class = GameForm
    success_message = "Game was successfully updated!"


class GameDeleteView(
    ModelPermissionMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    permission_action = "delete"
    template_name = "vault/games/confirm_delete.html"
    model = Game
    success_url = reverse_lazy("vault:game-list")
    success_message = "Game was successfully deleted!"
