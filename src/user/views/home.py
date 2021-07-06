from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import View
from constance import config
from authentication.models import User
from shared.models import ConfirmStatusChoices
from shared.statistics import UserPanelStatistics
from learning.models import Tutorial, TutorialView


class HomeView(View):
    def get(self, request: HttpRequest):
        latest_user_tutorials_count = 5

        latest_user_tutorials = (
            Tutorial.objects.filter(author=request.user)
            .prefetch_active_categories()
            .order_by("-create_date")[:latest_user_tutorials_count]
        )

        context = {
            "ConfirmStatusChoices": ConfirmStatusChoices,
            "statistics": self.get_statistics(),
            "latest_user_tutorials": latest_user_tutorials,
        }

        return render(request, "user/home.html", context)

    def get_statistics(self):
        user: User = self.request.user
        last_months_count = config.USER_PANEL_STATISTICS_LAST_MONTH_COUNT

        view_statistics = list(
            TutorialView.objects.filter(
                tutorial__author=user
            ).active_confirmed_tutorials()
            # get_last_months_count_statistics yields result
            .get_last_months_count_statistics(last_months_count)
        )

        tutorial_statistics = (
            Tutorial.objects.filter(author=user)
            .active_and_confirmed_tutorials()
            .aggregate_statistics()
        )

        return UserPanelStatistics(user, tutorial_statistics, view_statistics)
