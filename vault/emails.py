from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def build_activation_url(request, gamer):
    uid = urlsafe_base64_encode(force_bytes(gamer.pk))
    token = default_token_generator.make_token(gamer)
    path = reverse("vault:activate", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)


def send_activation_email(request, gamer):
    """Send the activation link (printed to the console in development)."""
    context = {
        "gamer": gamer,
        "activation_url": build_activation_url(request, gamer),
    }
    subject = render_to_string(
        "registration/activation_email_subject.txt",
        context,
    ).strip()
    body = render_to_string("registration/activation_email.txt", context)
    send_mail(subject, body, None, [gamer.email])
