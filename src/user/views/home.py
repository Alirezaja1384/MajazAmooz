from math import ceil
from django.shortcuts import render
from django.http import HttpRequest
from constance import config
from authentication.models import User
from shared.models import ConfirmStatusChoices
from shared.typed_dicts import TutorialStatistics
from learning.models import Tutorial, TutorialView


class UserPanelStatistics:
    def __init__(
        self,
        user: User,
        view_statistics: list[dict],
        tutorials_statistics: TutorialStatistics,
    ):
        # TODO: Make user goal statistics
        self.tutorials_count_goal = user.tutorials_count_goal
        self.comments_count_goal = user.comments_count_goal
        self.likes_count_goal = user.likes_count_goal
        self.views_count_goal = user.views_count_goal

        self.tutorials_statistics = tutorials_statistics
        self.view_statistics = view_statistics

    @staticmethod
    def __goal_completion_percent(count, goal_count):
        if goal_count == 0 or count > goal_count:
            return 100
        else:
            return ceil((count / goal_count) * 100)

    @property
    def tutorial_count_goal_percent(self):
        return self.__goal_completion_percent(
            self.tutorials_statistics["tutorials_count"],
            self.tutorials_count_goal,
        )

    @property
    def comments_count_goal_percent(self):
        return self.__goal_completion_percent(
            self.tutorials_statistics["comments_count"],
            self.comments_count_goal,
        )

    @property
    def likes_count_goal_percent(self):
        return self.__goal_completion_percent(
            self.tutorials_statistics["likes_count"], self.likes_count_goal
        )

    @property
    def views_count_goal_percent(self):
        return self.__goal_completion_percent(
            self.tutorials_statistics["views_count"], self.views_count_goal
        )


def get_view_statistics(user: User):
    last_months_count = config.USER_PANEL_STATISTICS_LAST_MONTH_COUNT

    all_views = TutorialView.objects.filter(
        tutorial__author=user
    ).active_confirmed_tutorials()

    return list(all_views.get_last_months_count_statistics(last_months_count))


def get_statistics(user: User):
    view_statistics = get_view_statistics(user)
    tutorial_statistics = (
        Tutorial.objects.filter(author=user)
        .active_and_confirmed_tutorials()
        .aggregate_statistics()
    )

    return UserPanelStatistics(user, view_statistics, tutorial_statistics)


def home_view(request: HttpRequest):
    latest_user_tutorials_count = 5

    latest_user_tutorials = (
        Tutorial.objects.filter(author=request.user)
        .prefetch_active_categories()
        .order_by("-create_date")[:latest_user_tutorials_count]
    )

    context = {
        "ConfirmStatusChoices": ConfirmStatusChoices,
        "statistics": get_statistics(request.user),
        "latest_user_tutorials": latest_user_tutorials,
    }

    return render(request, "user/home.html", context)
