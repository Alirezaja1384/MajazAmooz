""" Tutorial view """
from django.http import HttpRequest
from django.shortcuts import (
    render, get_object_or_404
)
from django.views.decorators.cache import cache_page

from ..models import Tutorial, Category


def get_tutorial_by_categories(categories: list[Category], fields: tuple,
                               tutorial_id: int, tutorial_count: int = 5) -> list[Tutorial]:
    """
    @param categories: categories to search tutorials by them
    @param fields: returns only specified fields of tutorial model
    @param tutorial_id: the main tutorial id to exclude
    @param tutorial_count: returns given count of tutorial
    @return: list of tutor tutorials
    """
    return Tutorial.objects.filter(is_active=True, confirm_status=1, categories__in=categories
                                   ).only(*fields).exclude(id=tutorial_id)[:tutorial_count]


def get_related_tutorials(tutorial: Tutorial, fields: tuple, tutorial_count: int = 5) -> list[Tutorial]:
    """
    @param tutorial: main tutorial
    @param fields: returns only specified fields of tutorial model
    @param tutorial_count: returns given count of tutorial
    @return: related tutorials by given tutorial object
    """

    # if tutorial doesn't have any active category return latest tutorials
    if not tutorial.categories.filter(is_active=True).count():
        return Tutorial.objects.filter(is_active=True, confirm_status=1)[tutorial_count]

    categories = []
    related_tutorials = []

    # while tutorials count are not enough and
    # there isn't any category in list
    # or all of categories are not None
    # (when all categories are none search will end)
    while len(related_tutorials) < tutorial_count and (not categories or
                                                       all(map(lambda cat: cat is not None, categories))):
        # when categories has at least one item
        if len(categories) > 0:
            # replace categories by their parent categories
            # if category is not None else return None
            categories = list(map(lambda cat: cat.parent_category if cat is not None else None, categories))
        # first time running this loop
        else:
            # Use tutorial categories for first time
            categories = tutorial.categories.filter(is_active=True).all()

        # categories that they're not None
        not_none_categories = list(filter(lambda cat: cat is not None, categories))

        # adds founded tutorials to related_tutorials list
        related_tutorials += get_tutorial_by_categories(not_none_categories, fields, tutorial.id,
                                                        tutorial_count - len(related_tutorials))

        # distinct related_tutorials
        related_tutorials = list(dict.fromkeys(related_tutorials))

    return related_tutorials


@cache_page(timeout=60 * 15)
def tutorial_details_view(request: HttpRequest, slug: str):
    """ Tutorial details view """
    tutorial = get_object_or_404(Tutorial.objects.filter(
        is_active=True, confirm_status=1).select_related('author'), slug=slug)

    comments = tutorial.comments.filter(is_active=True, confirm_status=1)

    related_tutorials = get_related_tutorials(tutorial, ('id', 'title', 'short_description', 'image'), 5)

    context = {
        "tutorial": tutorial,
        "comments": comments,
        "related_tutorials": related_tutorials
    }

    return render(request, 'learning/tutorial.html', context)
