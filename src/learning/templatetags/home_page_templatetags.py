""" Home page template tag """
from django import template
from learning.models import Tutorial

register = template.Library()


@register.inclusion_tag('learning/shared/tutorials_carousel.html')
def latest_tutorials(count: int = 5):
    """ Latest tutorials template tag """
    tutorials = Tutorial.objects.order_by('-create_date')[:count]

    return {
        "title": 'جدیدترین آموزش ها',
        "tutorials": tutorials
    }


@register.inclusion_tag('learning/shared/tutorials_carousel.html')
def most_liked_tutorials(count: int = 5):
    """ Latest tutorials template tag """
    tutorials = Tutorial.objects.order_by(
        '-likes_count', '-create_date')[:count]

    return {
        "gray_background": True,
        "title": 'محبوب ترین آموزش ها',
        "tutorials": tutorials
    }
