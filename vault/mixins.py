from django.views.generic.list import MultipleObjectMixin

from vault.forms import SearchForm


class SearchMixin(MultipleObjectMixin):
    """Adds a search box (?query=...) to a ListView."""

    search_field = "name"
    search_placeholder = "Search by name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = SearchForm(
            self.request.GET,
            placeholder=self.search_placeholder,
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = SearchForm(self.request.GET)
        if form.is_valid() and form.cleaned_data["query"]:
            lookup = {
                f"{self.search_field}__icontains": form.cleaned_data["query"]
            }
            queryset = queryset.filter(**lookup)
        return queryset
