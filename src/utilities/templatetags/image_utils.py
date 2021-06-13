"""
    Image utility templatetags
"""
from django import template
from django.db.models import ImageField
from django.templatetags.static import static
from django.utils.safestring import mark_safe

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
    except (ValueError, AttributeError):
        return static('img/not-found.png')


@register.simple_tag
def image_tag(image: ImageField, alt: str = '', max_width: int = 250, max_height: int = 250) -> str:
    """ Returns ImageField's image as a img tag if image exists
        else returns not-found image

    Args:
        image (ImageField): Image to create img tag
        alt (str, optional): Alternative text for image. Defaults to ''.
        max_width (int, optional): Max width of img tag (pixels). Defaults to 250.
        max_height (int, optional): Max height of img tag (pixels). Defaults to 250.

    Returns:
        str: img tag as a safe string
    """
    url = image_url(image)
    tag = (
        f'<a href="{url}"><img src="{url}" alt="{alt}" class="img-thumbnail"'
        f'style="max-width: {max_width}px; max-height: {max_height}px;"/></a>'
    )
    return mark_safe(tag)
