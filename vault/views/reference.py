from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.views import generic

from vault.mixins import (
    ModelPermissionMixin,
    ReferenceMixin,
    SearchMixin,
)
from vault.models import (
    Developer,
    Genre,
    Platform,
)


class ReferenceListView(
    LoginRequiredMixin,
    ReferenceMixin,
    SearchMixin,
    generic.ListView,
):
    template_name = "vault/reference/list.html"
    paginate_by = 10


class ReferenceCreateView(
    ModelPermissionMixin,
    ReferenceMixin,
    SuccessMessageMixin,
    generic.CreateView,
):
    permission_action = "add"
    template_name = "vault/reference/form.html"
    success_verb = "created"


class ReferenceUpdateView(
    ModelPermissionMixin,
    ReferenceMixin,
    SuccessMessageMixin,
    generic.UpdateView,
):
    permission_action = "change"
    template_name = "vault/reference/form.html"
    success_verb = "updated"


class ReferenceDeleteView(
    ModelPermissionMixin,
    ReferenceMixin,
    SuccessMessageMixin,
    generic.DeleteView,
):
    permission_action = "delete"
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
