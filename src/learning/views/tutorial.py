""" Tutorial view """
from django.http import HttpRequest
from django.views.decorators.csrf import requires_csrf_token
from django.db.models import Prefetch
from django.shortcuts import (
    render, get_object_or_404
)
from constance import config
from authentication.models import User
from learning.models import (
    Tutorial, Category,
    TutorialView
)


def get_tutorial_by_categories(categories: list[Category], fields: tuple,
                               tutorial_id: int, tutorial_count: int = 5) -> list[Tutorial]:
    """
    @param categories: categories to search tutorials by them
    @param fields: returns only specified fields of tutorial model
    @param tutorial_id: the main tutorial id to exclude
    @param tutorial_count: returns given count of tutorial
    @return: list of tutor tutorials
    """
    tutorials = Tutorial.objects.filter(categories__in=categories).only(
        *fields).exclude(id=tutorial_id).order_by(
            '-create_date').active_and_confirmed_tutorials().distinct()[:tutorial_count]

    return tutorials


def get_related_tutorials(tutorial: Tutorial, fields: tuple,
                          tutorial_count: int = 5) -> list[Tutorial]:
    """
    @param tutorial: main tutorial
    @param fields: returns only specified fields of tutorial model
    @param tutorial_count: returns given count of tutorial
    @return: related tutorials by given tutorial object
    """

    def _flat_categories_parents(categories: list[Category]):
        """ Returns list of categories and their parents """
        result = categories

        for category in categories:
            while category.parent_category:
                category = category.parent_category
                result.append(category)

        # Distinct result
        return list(dict.fromkeys(result))

    categories_and_parents = list(tutorial.categories.all())

    # If tutorial doesn't have any active category return empty
    if len(categories_and_parents) == 0:
        return Tutorial.objects.none()

    categories = _flat_categories_parents(categories_and_parents)

    # Get tutorials with joint categories
    related_tutorials = list(get_tutorial_by_categories(
        categories, fields, tutorial.id, tutorial_count))

    return related_tutorials


def record_tutorial_view(tutorial: Tutorial, user: User):
    """ Records tutorial's view

    Args:
        tutorial (Tutorial): visited tutorial
        user (User): user that visited the tutorial
    """
    tutorial_view_score = config.TUTORIAL_VIEW_SCORE
    tutorial_view_coin = config.TUTORIAL_VIEW_COIN

    if user.is_authenticated and not tutorial.views.filter(user=user).exists():

        TutorialView.objects.create(user=user, tutorial=tutorial,
                                    score=tutorial_view_score,
                                    coin=tutorial_view_coin)


@requires_csrf_token
def tutorial_details_view(request: HttpRequest, slug: str):
    """ Tutorial details view """
    tutorial = get_object_or_404(
        Tutorial.objects.select_related('author').prefetch_related(
            Prefetch('categories', queryset=Category.objects.active_categories())
        ).active_and_confirmed_tutorials(), slug=slug)
    tutorial.categories.select_related('parent_category')

    comments = tutorial.comments.select_related('parent_comment', 'user'
                                                ).active_and_confirmed_comments()

    related_tutorials = get_related_tutorials(
        tutorial, ('title', 'slug', 'short_description', 'image'), 5)

    # if user logged in and liked this tutorial
    liked_by_current_user = request.user.is_authenticated and tutorial.likes.filter(
        user_id=request.user.id).exists()

    all_tutorials = Tutorial.objects.active_and_confirmed_tutorials()

    latest_tutorials = all_tutorials.order_by('-create_date')[:4]
    most_popular_tutorials = all_tutorials.order_by('-likes_count')[:4]

    record_tutorial_view(tutorial, request.user)

    context = {
        'tutorial': tutorial,
        'liked_by_current_user': liked_by_current_user,
        'comments': comments,
        'tags': tutorial.tags.all(),
        # If there wasn't any related_tutorial use latest_tutorials instead
        'related_tutorials': related_tutorials or latest_tutorials,
        'latest_tutorials': latest_tutorials,
        'most_popular_tutorials': most_popular_tutorials
    }

    return render(request, 'learning/tutorial.html', context)
