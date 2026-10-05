from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views import generic

from vault.forms import (
    GamerCreationForm,
)


class RegisterView(generic.CreateView):
    form_class = GamerCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("vault:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        return response
