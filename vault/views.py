from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from vault.forms import GamerCreationForm
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


class GenreListView(LoginRequiredMixin, SearchMixin, generic.ListView):
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


class PlatformListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    queryset = Platform.objects.annotate(num_games=Count("games")).order_by(
        "name",
    )
    paginate_by = 10
    search_placeholder = "Search platforms"


class PlatformCreateView(
    LoginRequiredMixin, SuccessMessageMixin, generic.CreateView
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


class DeveloperListView(LoginRequiredMixin, SearchMixin, generic.ListView):
    queryset = Developer.objects.annotate(num_games=Count("games")).order_by(
        "name", "country"
    )
    paginate_by = 10
    search_placeholder = "Search developers"
