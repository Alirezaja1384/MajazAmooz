""" Tutorial view """
from django.http import HttpRequest
from django.shortcuts import (
    render, get_object_or_404
)
from django.views.decorators.cache import cache_page

from ..models import Tutorial


def get_related_tutorials(tutorial: Tutorial, fields: tuple, tutorial_count: int = 5) -> list[Tutorial]:
    """
    @param tutorial: main tutorial
    @param fields: returns only specified fields of tutorial model
    @param tutorial_count: returns given count of tutorial
    @return: related tutorials by given tutorial object
    """
    related_tutorials = []

    for category in tutorial.categories.filter(is_active=True):
        related_tutorials += category.tutorials.exclude(pk=tutorial.pk).only(*fields)[:tutorial_count]

        if len(related_tutorials) >= tutorial_count:
            break

    return related_tutorials


@cache_page(timeout=60*15)
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
