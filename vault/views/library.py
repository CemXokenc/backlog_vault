from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from vault.forms import (
    LibraryEntryForm,
)
from vault.mixins import (
    NextUrlMixin,
)
from vault.models import (
    Game,
    LibraryEntry,
)


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
