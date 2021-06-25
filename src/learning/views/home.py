""" Learn home view """
from django.db.models import Count, Q
from django.http import HttpRequest
from django.shortcuts import render


from shared.models import ConfirmStatusChoices

from learning.models import Tutorial


def get_tutorials(ordering: tuple, count: int):
    """
    Args:
        ordering (tuple): ordering of tutorials
        count (int): count of tutorials

    Returns:
        [TutorialQuerySet]: tutorials ordered by given ordering and
        sliced by given count
    """
    tutorials = Tutorial.objects.active_and_confirmed_tutorials().order_by(*ordering).only(
        'title', 'slug', 'short_description', 'likes_count', 'image')[:count].annotate(
        comments_count=Count('comments', filter=Q(
            comments__confirm_status=ConfirmStatusChoices.CONFIRMED)))

    return tutorials


def home_view(request: HttpRequest):
    """ Home view """

    carousel_count = 5

    latest_published_tutorials = get_tutorials(
        ordering=('-create_date',), count=carousel_count)

    most_liked_tutorials = get_tutorials(ordering=('-likes_count', '-create_date',),
                                         count=carousel_count)

    context = {
        "latest_published_tutorials": latest_published_tutorials,
        "most_liked_tutorials": most_liked_tutorials
    }

    return render(request, 'learning/home.html', context)
