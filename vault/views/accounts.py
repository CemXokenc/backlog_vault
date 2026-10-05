from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import generic
from django.views.decorators.http import require_POST

from vault.forms import GamerCreationForm
from vault.models import Gamer
from vault.roles import DEMO_USERS


class RegisterView(generic.CreateView):
    form_class = GamerCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("vault:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        return response


@require_POST
def demo_login(request, role):
    """Sign in as one of the demo users (only when DEMO_MODE is on)."""
    username = DEMO_USERS.get(role)
    if not settings.DEMO_MODE or username is None:
        raise Http404("Demo login is not available")
    gamer = get_object_or_404(Gamer, username=username)
    login(request, gamer, backend=settings.AUTHENTICATION_BACKENDS[0])
    messages.info(
        request,
        f"You are signed in as {gamer.username} (demo {role}).",
    )
    return redirect("vault:index")


def get_gamer_from_uid(uidb64):
    try:
        pk = force_str(urlsafe_base64_decode(uidb64))
        return Gamer.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, Gamer.DoesNotExist):
        return None


def activate(request, uidb64, token):
    """Activate the account from the emailed link and sign the gamer in."""
    gamer = get_gamer_from_uid(uidb64)
    if gamer is None or not default_token_generator.check_token(gamer, token):
        return render(
            request, "registration/activation_invalid.html", status=400
        )
    if not gamer.is_active:
        gamer.is_active = True
        gamer.save(update_fields=["is_active"])
    login(request, gamer, backend=settings.AUTHENTICATION_BACKENDS[0])
    messages.success(
        request, "Your account is active. Welcome to Backlog Vault!"
    )
    return redirect("vault:index")
