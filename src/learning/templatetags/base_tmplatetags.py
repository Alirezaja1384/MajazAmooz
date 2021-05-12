""" Base template template-tags """

from django import template

from learning.models import Category


register = template.Library()


@register.inclusion_tag('shared/navbar_categories.html')
def navbar_tutorial_categories():
    """ Navbar categories template-tag """

    categories = Category.objects.select_related(
        'parent_category').order_by('parent_category').active_categories()
    return {"categories": categories}


@register.filter
def is_in_parents(category: Category, categories: list[Category]) -> bool:
    """ Template filter to know is a category a parent category or not

    Args:
        category (Category): Category that want to search it in parents
        categories (list[Category]): Categories want to search in their parents

    Returns:
        bool: True if category is one of categories' parents and False if not
    """
    return any(filter(lambda cat: cat.parent_category == category, categories))
