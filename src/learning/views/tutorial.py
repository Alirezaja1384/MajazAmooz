""" Tutorial view """
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from django.views.decorators.csrf import requires_csrf_token
from constance import config
from learning.models import Tutorial, TutorialView


@method_decorator(requires_csrf_token, name="dispatch")
class TutorialDetailsView(View):
    """Tutorial details view"""

    def get(self, request: HttpRequest, slug: str):
        all_tutorials = Tutorial.objects.active_and_confirmed_tutorials()

        tutorial: Tutorial = get_object_or_404(
            all_tutorials.select_related("author")
            .prefetch_related("tags")
            .prefetch_active_categories()
            .prefetch_active_confirmed_comments(),
            slug=slug,
        )

        related_tutorials = all_tutorials.get_related_tutorials(
            tutorial
        ).only_main_fields()

        # Check is user logged in and liked this tutorial
        liked_by_current_user = (
            request.user.is_authenticated
            and tutorial.likes.filter(user=request.user).exists()
        )
        latest_tutorials = all_tutorials.order_by("-create_date")[:4]
        most_popular_tutorials = all_tutorials.order_by("-likes_count")[:4]

        context = {
            "tutorial": tutorial,
            "liked_by_current_user": liked_by_current_user,
            "comments": tutorial.comments.all(),
            "tags": tutorial.tags.all(),
            # If there wasn't any related_tutorial use latest_tutorials instead
            "related_tutorials": related_tutorials or latest_tutorials,
            "latest_tutorials": latest_tutorials,
            "most_popular_tutorials": most_popular_tutorials,
        }

        self.record_tutorial_view(tutorial)
        return render(request, "learning/tutorial.html", context)

    def record_tutorial_view(self, tutorial: Tutorial):
        """Records tutorial's view.

        Args:
            tutorial (Tutorial): Visited tutorial
            user (User): User that visited the tutorial
        """
        tutorial_view_score = config.TUTORIAL_VIEW_SCORE
        tutorial_view_coin = config.TUTORIAL_VIEW_COIN

        user = self.request.user
        if (
            user.is_authenticated
            and not tutorial.views.filter(user=user).exists()
        ):
            TutorialView.objects.create(
                user=user,
                tutorial=tutorial,
                score=tutorial_view_score,
                coin=tutorial_view_coin,
            )
