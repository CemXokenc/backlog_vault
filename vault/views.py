from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Avg, Sum
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.http import require_POST

from vault.forms import (
    GamerCreationForm,
    GameFilterForm,
    GameForm,
    LibraryEntryForm,
    CollectionForm,
    GamerUpdateForm,
)
from vault.mixins import (
    NextUrlMixin,
    ReferenceMixin,
    SearchMixin,
    get_safe_next_url,
)
from vault.models import (
    LibraryEntry,
    Game,
    Genre,
    Platform,
    Developer,
    Collection,
    Gamer,
)


@login_required
def index(request):
    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    my_library = LibraryEntry.objects.filter(gamer=request.user).aggregate(
        total=Count("id"),
        playing=Count("id", filter=Q(status=LibraryEntry.Status.PLAYING)),
        completed=Count("id", filter=Q(status=LibraryEntry.Status.COMPLETED)),
    )

    context = {
        "num_visits": num_visits,
        "num_games": Game.objects.count(),
        "num_genres": Genre.objects.count(),
        "num_platforms": Platform.objects.count(),
        "num_developers": Developer.objects.count(),
        "num_collections": Collection.objects.count(),
        "num_gamers": Gamer.objects.count(),
        "my_library": my_library,
    }

    return render(request, "vault/home.html", context=context)


class RegisterView(generic.CreateView):
    form_class = GamerCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("vault:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        return response


class ReferenceListView(
    LoginRequiredMixin,
    ReferenceMixin,
    SearchMixin,
    generic.ListView,
):
    template_name = "vault/reference/list.html"
    paginate_by = 10


class ReferenceCreateView(
    LoginRequiredMixin,
    ReferenceMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    template_name = "vault/reference/form.html"
    success_verb = "created"


class ReferenceUpdateView(
    LoginRequiredMixin,
    ReferenceMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    template_name = "vault/reference/form.html"
    success_verb = "updated"


class ReferenceDeleteView(
    LoginRequiredMixin,
    ReferenceMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    template_name = "vault/reference/confirm_delete.html"
    success_verb = "deleted"


class GenreListView(ReferenceListView):
    model = Genre
    queryset = Genre.objects.annotate(num_games=Count("games")).order_by(
        "name",
    )
    url_prefix = "genre"
    search_placeholder = "Search genres"


class GenreCreateView(ReferenceCreateView):
    model = Genre
    fields = ["name"]
    url_prefix = "genre"


class GenreUpdateView(ReferenceUpdateView):
    model = Genre
    fields = ["name"]
    url_prefix = "genre"


class GenreDeleteView(ReferenceDeleteView):
    model = Genre
    url_prefix = "genre"
    delete_hint = (
        "will stay in the catalog but lose this genre. "
        "Gamers who chose it as their favorite will have that field cleared."
    )


class PlatformListView(ReferenceListView):
    model = Platform
    queryset = Platform.objects.annotate(num_games=Count("games")).order_by(
        "name",
    )
    url_prefix = "platform"
    search_placeholder = "Search platforms"


class PlatformCreateView(ReferenceCreateView):
    model = Platform
    fields = ["name"]
    url_prefix = "platform"


class PlatformUpdateView(ReferenceUpdateView):
    model = Platform
    fields = ["name"]
    url_prefix = "platform"


class PlatformDeleteView(ReferenceDeleteView):
    model = Platform
    url_prefix = "platform"
    delete_hint = (
        "will stay in the catalog but lose this platform. "
        "Library entries that used it will simply have no platform."
    )


class DeveloperListView(ReferenceListView):
    model = Developer
    queryset = Developer.objects.annotate(num_games=Count("games")).order_by(
        "name",
        "country",
    )
    url_prefix = "developer"
    show_country = True
    search_placeholder = "Search developers"


class DeveloperCreateView(ReferenceCreateView):
    model = Developer
    fields = ["name", "country"]
    url_prefix = "developer"


class DeveloperUpdateView(ReferenceUpdateView):
    model = Developer
    fields = ["name", "country"]
    url_prefix = "developer"


class DeveloperDeleteView(ReferenceDeleteView):
    model = Developer
    url_prefix = "developer"
    delete_hint = "will stay in the catalog without a developer."


class GameListView(
    LoginRequiredMixin,
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
    LoginRequiredMixin,
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
        context["entries"] = LibraryEntry.objects.filter(
            game=self.object,
        ).select_related("gamer", "platform")
        context["my_entry"] = LibraryEntry.objects.filter(
            gamer=self.request.user,
            game=self.object,
        ).first()
        context["game_collections"] = self.object.collections.select_related(
            "owner",
        )
        my_collections = Collection.objects.filter(owner=self.request.user)
        context["addable_collections"] = my_collections.exclude(
            games=self.object,
        )
        context["removable_collections"] = my_collections.filter(
            games=self.object,
        )

        return context


class GameCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    template_name = "vault/games/form.html"
    model = Game
    form_class = GameForm
    success_message = "Game was successfully created!"


class GameUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    template_name = "vault/games/form.html"
    model = Game
    form_class = GameForm
    success_message = "Game was successfully updated!"


class GameDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    template_name = "vault/games/confirm_delete.html"
    model = Game
    success_url = reverse_lazy("vault:game-list")
    success_message = "Game was successfully deleted!"


class LibraryEntryListView(
    LoginRequiredMixin,
    generic.ListView,
):
    template_name = "vault/library/list.html"
    context_object_name = "entries"
    paginate_by = 10

    def get_queryset(self):
        queryset = (
            LibraryEntry.objects.filter(gamer=self.request.user)
            .select_related("game", "platform")
            .order_by("-id")
        )
        status = self.request.GET.get("status")
        if status in LibraryEntry.Status.values:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        counts = dict(
            LibraryEntry.objects.filter(gamer=self.request.user)
            .order_by()
            .values_list("status")
            .annotate(total=Count("id")),
        )
        tabs = [{"status": "", "label": "All", "count": sum(counts.values())}]

        for status, label in LibraryEntry.Status.choices:
            tabs.append(
                {
                    "status": status,
                    "label": label,
                    "count": counts.get(status, 0),
                },
            )
        current_status = self.request.GET.get("status", "")
        if current_status not in LibraryEntry.Status.values:
            current_status = ""
        context["tabs"] = tabs
        context["current_status"] = current_status

        return context


class LibraryEntryCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    NextUrlMixin,
    generic.CreateView,
):
    template_name = "vault/library/form.html"
    model = LibraryEntry
    form_class = LibraryEntryForm
    success_message = "Game was added to your library!"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.game = get_object_or_404(Game, pk=kwargs["game_pk"])
            existing = LibraryEntry.objects.filter(
                gamer=request.user,
                game=self.game,
            ).first()
            if existing:
                messages.info(request, "This game is already in your library.")
                return redirect("vault:library-update", pk=existing.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = LibraryEntry(
            gamer=self.request.user,
            game=self.game,
        )

        return kwargs

    def get_success_url(self):
        return self.get_next_url() or self.game.get_absolute_url()


class LibraryEntryUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    NextUrlMixin,
    generic.UpdateView,
):
    template_name = "vault/library/form.html"
    model = LibraryEntry
    form_class = LibraryEntryForm
    success_url = reverse_lazy("vault:library-list")
    success_message = "Library entry was updated!"

    def get_queryset(self):
        return LibraryEntry.objects.filter(
            gamer=self.request.user,
        ).select_related("game")


class LibraryEntryDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    NextUrlMixin,
    generic.DeleteView,
):
    template_name = "vault/library/confirm_delete.html"
    model = LibraryEntry
    success_url = reverse_lazy("vault:library-list")
    success_message = "Game was removed from your library."

    def get_queryset(self):
        return LibraryEntry.objects.filter(
            gamer=self.request.user,
        ).select_related("game")


class CollectionListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    template_name = "vault/collections/list.html"
    queryset = (
        Collection.objects.select_related("owner")
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


def redirect_back(request, fallback):
    return redirect(get_safe_next_url(request) or fallback)


@login_required
@require_POST
def collection_add_game(request, pk):
    collection = get_object_or_404(Collection, pk=pk, owner=request.user)
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
    return redirect_back(request, collection)


@login_required
@require_POST
def collection_remove_game(request, pk, game_pk):
    collection = get_object_or_404(Collection, pk=pk, owner=request.user)
    game = get_object_or_404(Game, pk=game_pk)
    collection.games.remove(game)
    messages.success(
        request,
        f"{game.title} was removed from {collection.title}.",
    )

    return redirect_back(request, collection)


class GamerListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    template_name = "vault/gamers/list.html"
    queryset = (
        Gamer.objects.select_related("favorite_genre")
        .annotate(
            num_games=Count("library_entries"),
            num_completed=Count(
                "library_entries",
                filter=Q(
                    library_entries__status=LibraryEntry.Status.COMPLETED,
                ),
            ),
        )
        .order_by("username")
    )
    search_field = "username"
    search_placeholder = "Search by username"
    paginate_by = 9


class GamerDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "vault/gamers/detail.html"
    queryset = Gamer.objects.select_related("favorite_genre")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = LibraryEntry.objects.filter(gamer=self.object)
        status = LibraryEntry.Status
        stats = entries.order_by().aggregate(
            total=Count("id"),
            planned=Count("id", filter=Q(status=status.PLANNED)),
            playing=Count("id", filter=Q(status=status.PLAYING)),
            completed=Count("id", filter=Q(status=status.COMPLETED)),
            dropped=Count("id", filter=Q(status=status.DROPPED)),
            hours=Sum("hours_played"),
            avg_rating=Avg("rating"),
        )
        stats["hours"] = stats["hours"] or 0
        context["stats"] = stats
        context["top_genre"] = (
            Genre.objects.filter(games__library_entries__gamer=self.object)
            .annotate(num_games=Count("games", distinct=True))
            .order_by("-num_games", "name")
            .first()
        )
        context["recent_entries"] = entries.select_related("game").order_by(
            "-id",
        )[:5]
        context["collections"] = self.object.collections.annotate(
            num_games=Count("games"),
        )
        context["is_me"] = self.object.pk == self.request.user.pk

        return context


class GamerUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    template_name = "vault/gamers/form.html"
    model = Gamer
    form_class = GamerUpdateForm
    success_message = "Profile was updated!"

    def get_queryset(self):
        return Gamer.objects.filter(pk=self.request.user.pk)
