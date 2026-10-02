from django.contrib.auth.forms import UserCreationForm

from vault.models import Gamer


class GamerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Gamer
        fields = UserCreationForm.Meta.fields + (
            "nickname",
            "favorite_genre",
        )
