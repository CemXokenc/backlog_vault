from django.urls import path

from vault.views import index

urlpatterns = [
    path("", index, name="index"),
]

app_name = "vault"
