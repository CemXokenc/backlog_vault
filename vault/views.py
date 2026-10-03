from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q, Avg
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from vault.forms import GamerCreationForm, GameFilterForm, GameForm
from vault.mixins import SearchMixin
from vault.models import LibraryEntry, Game, Genre, Platform, Developer


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
        "my_library": my_library,
    }

    return render(request, "vault/index.html", context=context)


class RegisterView(generic.CreateView):
    form_class = GamerCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("vault:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        return response


class GenreListView(
    LoginRequiredMixin,
    SearchMixin,
    generic.ListView,
):
    queryset = Genre.objects.annotate(num_games=Count("games")).order_by(
        "name",
    )
    paginate_by = 10
    search_placeholder = "Search genres"


class GenreCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    model = Genre
    fields = ["name"]
    success_url = reverse_lazy("vault:genre-list")
    success_message = "Genre was successfully created!"


class GenreUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    model = Genre
    fields = ["name"]
    success_url = reverse_lazy("vault:genre-list")
    success_message = "Genre was successfully updated!"


class GenreDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    model = Genre
    success_url = reverse_lazy("vault:genre-list")
    success_message = "Genre was successfully deleted!"


class PlatformListView(
    LoginRequiredMixin,
    SearchMixin,
    generic.ListView,
):
    queryset = Platform.objects.annotate(num_games=Count("games")).order_by(
        "name",
    )
    paginate_by = 10
    search_placeholder = "Search platforms"


class PlatformCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    model = Platform
    fields = ["name"]
    success_url = reverse_lazy("vault:platform-list")
    success_message = "Platform was successfully created!"


class PlatformUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    model = Platform
    fields = ["name"]
    success_url = reverse_lazy("vault:platform-list")
    success_message = "Platform was successfully updated!"


class PlatformDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    model = Platform
    success_url = reverse_lazy("vault:platform-list")
    success_message = "Platform was successfully deleted!"


class DeveloperListView(
    LoginRequiredMixin,
    SearchMixin,
    generic.ListView,
):
    queryset = Developer.objects.annotate(num_games=Count("games")).order_by(
        "name",
        "country",
    )
    paginate_by = 10
    search_placeholder = "Search developers"


class DeveloperCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    model = Developer
    fields = ["name", "country"]
    success_url = reverse_lazy("vault:developer-list")
    success_message = "Developer was successfully created!"


class DeveloperUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    model = Developer
    fields = ["name", "country"]
    success_url = reverse_lazy("vault:developer-list")
    success_message = "Developer was successfully updated!"


class DeveloperDeleteView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    model = Developer
    success_url = reverse_lazy("vault:developer-list")
    success_message = "Developer was successfully deleted!"


class GameListView(
    LoginRequiredMixin,
    SearchMixin,
    generic.ListView,
):
    queryset = (
        Game.objects.select_related("developer")
        .prefetch_related("genres")
        .annotate(
            avg_rating=Avg("library_entries__rating"),
            num_players=Count("library_entries"),
        )
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
    queryset = (
        Game.objects.select_related("developer")
        .prefetch_related("genres", "platforms")
        .annotate(
            avg_rating=Avg("library_entries__rating"),
            num_players=Count("library_entries"),
        )
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entries"] = LibraryEntry.objects.filter(
            game=self.object,
        ).select_related("gamer", "platform")

        return context


class GameCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    model = Game
    form_class = GameForm
    success_message = "Game was successfully created!"


class GameUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    model = Game
    form_class = GameForm
    success_message = "Game was successfully updated!"
