""" Home page template tag """
from django import template
from django.db.models import Count, Q
from learning.models import Tutorial

register = template.Library()


def get_tutorials(ordering: tuple, count: int):
    """
    Args:
        ordering (tuple): orderby given fields
        count (int): count of tutorials

    Returns:
        [TutorialQuerySet]: tutorials ordered by given ordering and
        sliced by given count
    """
    tutorials = Tutorial.objects.confirmed_tutorials().order_by(*ordering).values(
        'title', 'slug', 'short_description', 'likes_count')[:count].annotate(
        comments_count=Count('comments', filter=Q(comments__confirm_status=1)))

    return tutorials


@register.inclusion_tag('learning/shared/tutorials_carousel.html')
def latest_tutorials(count: int = 5):
    """ Latest tutorials template tag """
    return {
        "title": 'جدیدترین آموزش ها',
        "tutorials": get_tutorials(ordering=('-create_date',), count=count)
    }


@register.inclusion_tag('learning/shared/tutorials_carousel.html')
def most_liked_tutorials(count: int = 5):
    """ Latest tutorials template tag """
    return {
        "gray_background": True,
        "title": 'محبوب ترین آموزش ها',
        "tutorials": get_tutorials(ordering=('-likes_count', '-create_date',), count=count)
    }
