from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from vault.forms import SearchForm


def get_safe_next_url(request):
    """Return the `next` URL (POST or GET) if it points to this site."""
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return next_url
    return ""


class NextUrlMixin(FormMixin):
    """Sends the user back to the page they came from (?next=...)."""

    def get_next_url(self):
        return get_safe_next_url(self.request)

    def get_success_url(self):
        return self.get_next_url() or super().get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.get_next_url()
        return context


class SearchMixin(MultipleObjectMixin):
    """Adds a search box (?query=...) to a ListView."""

    form_class = SearchForm
    search_field = "name"
    search_placeholder = "Search by name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = self.form_class(
            self.request.GET,
            placeholder=self.search_placeholder,
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.form_class(self.request.GET)
        if form.is_valid() and form.cleaned_data["query"]:
            lookup = {
                f"{self.search_field}__icontains": form.cleaned_data["query"]
            }
            queryset = queryset.filter(**lookup)
        return queryset


class ReferenceMixin(ContextMixin):
    """Shared behaviour of the genre, platform and developer pages."""

    model = None
    url_prefix = ""
    delete_hint = ""
    show_country = False
    success_verb = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opts = self.model._meta
        route = f"vault:{self.url_prefix}"
        context["ref"] = {
            "title": opts.verbose_name.title(),
            "title_plural": opts.verbose_name_plural.title(),
            "list_url": reverse(f"{route}-list"),
            "create_url": reverse(f"{route}-create"),
            "update_name": f"{route}-update",
            "delete_name": f"{route}-delete",
            "delete_hint": self.delete_hint,
            "show_country": self.show_country,
        }
        return context

    def get_success_url(self):
        return reverse(f"vault:{self.url_prefix}-list")

    def get_success_message(self, cleaned_data):
        name = self.model._meta.verbose_name.title()
        return f"{name} was successfully {self.success_verb}!"


class ModelPermissionMixin(PermissionRequiredMixin):
    """Requires the model permission that matches `permission_action`.

    For example `permission_action = "add"` on a Game view requires
    `vault.add_game`. Guests are sent to the login page, signed-in users
    without the permission get a 403 page.
    """

    permission_action = "view"

    def get_permission_required(self):
        opts = self.model._meta
        return (
            f"{opts.app_label}.{self.permission_action}_{opts.model_name}",
        )
