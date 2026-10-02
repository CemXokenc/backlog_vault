from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from vault.forms import GamerCreationForm
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
