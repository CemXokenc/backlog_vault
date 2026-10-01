from datetime import datetime

from django.core.exceptions import ValidationError

MIN_RELEASE_YEAR = 1960
MIN_RATING = 1
MAX_RATING = 10


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


def validate_rating(value: int) -> None:
    """Validates that the rating is within allowable bounds."""
    if value < MIN_RATING or value > MAX_RATING:
        raise ValidationError(
            f"Rating can't be less than {MIN_RATING} "
            f"or greater than {MAX_RATING}.",
        )
