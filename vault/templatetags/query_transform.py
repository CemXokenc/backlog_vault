from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """Return the current GET query string with the given params replaced."""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
