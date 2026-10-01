from datetime import datetime

from django.core.exceptions import ValidationError

MIN_RELEASE_YEAR = 1960


def current_year():
    """Returns the current calendar year."""
    return datetime.now().year


def validate_release_year(value: int) -> None:
    """Validates that release_year is within allowable bounds."""
    current = current_year()
    if value < MIN_RELEASE_YEAR:
        raise ValidationError(
            f"Release year can't be less than {MIN_RELEASE_YEAR}.",
        )
    if value > current:
        raise ValidationError(
            f"Release year can't be greater than current ({current}).",
        )
