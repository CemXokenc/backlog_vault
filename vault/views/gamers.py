from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Avg, Count, Q, Sum
from django.views import generic

from vault.forms import (
    GamerUpdateForm,
)
from vault.mixins import (
    SearchMixin,
)
from vault.models import (
    Gamer,
    Genre,
    LibraryEntry,
)


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
