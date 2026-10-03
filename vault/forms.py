from django.contrib.auth.forms import UserCreationForm
from django import forms

from vault.models import Gamer, Genre, Platform, Game


class GamerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Gamer
        fields = UserCreationForm.Meta.fields + (
            "nickname",
            "favorite_genre",
        )


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, placeholder="Search...", **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["query"].widget.attrs["placeholder"] = placeholder


class GameFilterForm(SearchForm):
    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All genres",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        empty_label="All platforms",
        widget=forms.Select(attrs={"class": "form-control"}),
    )


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "title",
            "release_year",
            "developer",
            "genres",
            "platforms",
            "description",
            "cover_url",
        ]
        widgets = {
            "genres": forms.CheckboxSelectMultiple,
            "platforms": forms.CheckboxSelectMultiple,
            "description": forms.Textarea(attrs={"rows": 4}),
        }
