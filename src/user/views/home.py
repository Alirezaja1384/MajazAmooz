from math import ceil

from django.shortcuts import render
from django.http import HttpRequest
from django.db.models import Prefetch

from authentication.models import User
from utilities.model_utils import ConfirmStatusChoices
from utilities.date_time import get_last_months
from learning.models import (
    Tutorial, Category, TutorialComment,
    TutorialLike, TutorialView
)


class UserStatistics:
    def __init__(self, tutorials_count, comments_count, likes_count, views_count,
                 user: User, view_statistics: list[dict]):
        self.tutorials_count = tutorials_count
        self.comments_count = comments_count
        self.likes_count = likes_count
        self.views_count = views_count
        self.tutorials_count_goal = user.tutorials_count_goal
        self.comments_count_goal = user.comments_count_goal
        self.likes_count_goal = user.likes_count_goal
        self.views_count_goal = user.views_count_goal

        self.view_statistics = view_statistics

    @staticmethod
    def __goal_completion_percent(count, goal_count):
        if goal_count == 0 or count > goal_count:
            return 100
        else:
            return ceil((count / goal_count) * 100)

    @property
    def tutorial_count_goal_percent(self):
        return self.__goal_completion_percent(self.tutorials_count, self.tutorials_count_goal)

    @property
    def comments_count_goal_percent(self):
        return self.__goal_completion_percent(self.comments_count, self.comments_count_goal)

    @property
    def likes_count_goal_percent(self):
        return self.__goal_completion_percent(self.likes_count, self.likes_count_goal)

    @property
    def views_count_goal_percent(self):
        return self.__goal_completion_percent(self.views_count, self.views_count_goal)


# TODO: Make last_months_count dynamic
def get_view_statistics(user: User):
    last_months_count = 5

    all_views = TutorialView.objects.filter(
        tutorial__author=user).active_confirmed_tutorials()
    last_months = get_last_months(last_months_count)

    result = []
    for month in last_months:
        result.append({
            'label': month.label,
            'count': all_views.filter(create_date__gte=month.gregorian_start,
                                      create_date__lte=month.gregorian_end).count()
        })

    return result


def get_user_statistics(user: User):

    tutorials_count = Tutorial.objects.filter(
        author=user).active_and_confirmed_tutorials().count()

    comments_count = TutorialComment.objects.filter(
        tutorial__author=user).active_confirmed_tutorials(
    ).active_and_confirmed_comments().count()

    likes_count = TutorialLike.objects.active_confirmed_tutorials().filter(
        tutorial__author=user).count()

    views_count = TutorialView.objects.active_confirmed_tutorials().filter(
        tutorial__author=user).count()

    return UserStatistics(tutorials_count, comments_count, likes_count, views_count,
                          user, get_view_statistics(user))


def home_view(request: HttpRequest):
    latest_user_tutorials_count = 5

    latest_user_tutorials = Tutorial.objects.filter(author=request.user).prefetch_related(
        Prefetch('categories', queryset=Category.objects.active_categories())
    ).order_by('-create_date')[:latest_user_tutorials_count]

    context = {
        'ConfirmStatusChoices': ConfirmStatusChoices,
        'statistics': get_user_statistics(request.user),
        'latest_user_tutorials': latest_user_tutorials,
    }

    return render(request, 'user/home.html', context)
