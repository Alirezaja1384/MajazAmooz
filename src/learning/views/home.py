""" Learn home view """
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import View
from constance import config
from learning.models import Tutorial


class HomeView(View):
    """Home view"""

    def get(self, request: HttpRequest):
        carousel_count = config.LEARNING_HOME_CAROUSEL_ITEMS_COUNT

        tutorials = (
            Tutorial.objects.active_and_confirmed_tutorials()
            .only_main_fields()
            .annonate_comments_count()
        )

        latest_published_tutorials = tutorials.order_by(
            "-create_date",
        )[:carousel_count]

        most_liked_tutorials = tutorials.order_by(
            "-likes_count",
            "-create_date",
        )[:carousel_count]

        context = {
            "latest_published_tutorials": latest_published_tutorials,
            "most_liked_tutorials": most_liked_tutorials,
        }

        return render(request, "learning/home.html", context)
