from django.urls import path

from vault.views import index, RegisterView

urlpatterns = [
    path("", index, name="index"),
    path("/register", RegisterView.as_view(), name="register"),
]

app_name = "vault"
