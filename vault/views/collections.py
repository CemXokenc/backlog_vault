from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from vault.forms import (
    CollectionForm,
    CommentForm,
)
from vault.mixins import (
    SearchMixin,
    get_safe_next_url,
)
from vault.models import (
    Collection,
    Game,
)


class CollectionListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    template_name = "vault/collections/list.html"
    queryset = (
        Collection.objects.select_related("owner")
        .prefetch_related("games")
        .annotate(num_games=Count("games"))
        .order_by("title")
    )
    search_field = "title"
    search_placeholder = "Search collections"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("mine"):
            queryset = queryset.filter(owner=self.request.user)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mine"] = bool(self.request.GET.get("mine"))

        return context


class CollectionDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "vault/collections/detail.html"
    queryset = Collection.objects.select_related("owner")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_owner = self.object.owner_id == self.request.user.pk
        context["is_owner"] = is_owner
        context["comments"] = self.object.comments.select_related("author")
        context["comment_form"] = CommentForm()
        context["games"] = (
            self.object.games.select_related("developer")
            .prefetch_related("genres")
            .with_stats()
            .order_by("-release_year", "title")
        )
        if is_owner:
            context["available_games"] = Game.objects.exclude(
                collections=self.object,
            ).order_by("title")

        return context


class CollectionCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    template_name = "vault/collections/form.html"
    model = Collection
    form_class = CollectionForm
    success_message = "Collection was created!"

    def form_valid(self, form):
        form.instance.owner = self.request.user

        return super().form_valid(form)


class CollectionUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    template_name = "vault/collections/form.html"
    model = Collection
    form_class = CollectionForm
    success_message = "Collection was updated!"

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)


class CollectionDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    template_name = "vault/collections/confirm_delete.html"
    model = Collection
    success_url = reverse_lazy("vault:collection-list")
    success_message = "Collection was deleted."

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)


class CollectionGameView(LoginRequiredMixin, SingleObjectMixin, generic.View):
    """Base of the POST-only views that add or remove a collection game."""

    def get_queryset(self):
        return Collection.objects.filter(owner=self.request.user)

    def redirect_back(self, collection):
        return redirect(get_safe_next_url(self.request) or collection)


class CollectionAddGameView(CollectionGameView):
    def post(self, request, *args, **kwargs):
        collection = self.get_object()
        game_pk = request.POST.get("game", "")
        if not game_pk.isdigit():
            raise Http404("Game not found")
        game = get_object_or_404(Game, pk=game_pk)
        if collection.games.filter(pk=game.pk).exists():
            messages.info(
                request,
                f"{game.title} is already in {collection.title}.",
            )
        else:
            collection.games.add(game)
            messages.success(
                request,
                f"{game.title} was added to {collection.title}.",
            )

        return self.redirect_back(collection)


class CollectionRemoveGameView(CollectionGameView):
    def post(self, request, *args, **kwargs):
        collection = self.get_object()
        game = get_object_or_404(Game, pk=kwargs["game_pk"])
        collection.games.remove(game)
        messages.success(
            request,
            f"{game.title} was removed from {collection.title}.",
        )

        return self.redirect_back(collection)
