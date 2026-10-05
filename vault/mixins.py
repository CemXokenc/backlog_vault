from django.utils.http import url_has_allowed_host_and_scheme
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
