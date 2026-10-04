from django.contrib.auth.forms import UserCreationForm
from django import forms

from vault.models import Gamer, Genre, Platform, Game, LibraryEntry, Collection


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
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        empty_label="All platforms",
        widget=forms.Select(attrs={"class": "form-select"}),
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


class LibraryEntryForm(forms.ModelForm):
    class Meta:
        model = LibraryEntry
        fields = [
            "status",
            "platform",
            "rating",
            "hours_played",
            "started_at",
            "finished_at",
            "note",
        ]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 10}),
            "hours_played": forms.NumberInput(attrs={"min": 0}),
            "started_at": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "finished_at": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "note": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.game_id:
            self.fields["platform"].queryset = (
                self.instance.game.platforms.all()
            )

    def clean(self):
        super().clean()
        started_at = self.cleaned_data.get("started_at")
        finished_at = self.cleaned_data.get("finished_at")
        if started_at and finished_at and finished_at < started_at:
            self.add_error(
                "finished_at",
                "Finish date can't be earlier than the start date.",
            )

        return self.cleaned_data


class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ["title", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class GamerUpdateForm(forms.ModelForm):
    class Meta:
        model = Gamer
        fields = ["nickname", "bio", "favorite_genre"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}
