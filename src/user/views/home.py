from math import ceil
from django.shortcuts import render
from django.http import HttpRequest

from authentication.models import User
from learning.models import (
    Tutorial, TutorialComment,
    TutorialLike, TutorialView
)


class UserStatistics:
    def __init__(self, tutorials_count, comments_count, likes_count, views_count, user: User):
        self.tutorials_count = tutorials_count
        self.comments_count = comments_count
        self.likes_count = likes_count
        self.views_count = views_count
        self.tutorials_count_goal = user.tutorials_count_goal
        self.comments_count_goal = user.comments_count_goal
        self.likes_count_goal = user.likes_count_goal
        self.views_count_goal = user.views_count_goal

    @property
    def tutorial_count_goal_percent(self):
        return ceil(self.tutorials_count / self.tutorials_count_goal * 100)

    @property
    def comments_count_goal_percent(self):
        return ceil(self.comments_count / self.comments_count_goal * 100)

    @property
    def likes_count_goal_percent(self):
        return ceil(self.likes_count / self.likes_count_goal * 100)

    @property
    def views_count_goal_percent(self):
        return ceil(self.views_count / self.views_count_goal * 100)


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

    return UserStatistics(tutorials_count, comments_count, likes_count, views_count, user)


def home_view(request: HttpRequest):
    context = {
        'statistics': get_user_statistics(request.user)
    }
    return render(request, 'user/home.html', context)
