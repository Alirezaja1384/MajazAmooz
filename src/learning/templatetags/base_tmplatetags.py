""" Base template template-tags """

from django import template
from learning.models import Category

register = template.Library()


@register.inclusion_tag('shared/navbar_categories.html')
def navbar_tutorial_categories():
    """ Navbar categories template-tag """
    return {
        "categories": Category.objects.filter(is_active=True).prefetch_related(
            'child_categories').order_by('parent_category').all()
    }
