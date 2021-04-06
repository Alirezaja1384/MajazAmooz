"""
    Image utility templatetags
"""
from django import template
from django.db.models import ImageField
from django.templatetags.static import static

register = template.Library()


@register.filter
def image_url(image: ImageField) -> str:
    """
    Returns ImageField's url if exist
    else returns not-found image

    @param image: image
    @return: image url
    """
    try:
        return image.url
    except ValueError:
        return static('img/not-found.png')
