"""
    TutorialComment-User many to many relation models
"""
from django.db import models

from authentication.models import User

from . import TutorialComment


class TutorialCommentLike(models.Model):
    """ TutorialCommentLike model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tutorial_comment_likes', verbose_name='کاربر')

    comment = models.ForeignKey(
        TutorialComment, on_delete=models.CASCADE,
        related_name='likes', verbose_name='نظر آموزش')

    score = models.PositiveIntegerField(verbose_name='امتیاز')

    coin = models.PositiveIntegerField(verbose_name='سکه')


class TutorialCommentUpVote(models.Model):
    """ TutorialCommentUpVote model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tutorial_comment_up_votes',
        verbose_name='کاربر')

    comment = models.ForeignKey(
        TutorialComment, on_delete=models.CASCADE,
        related_name='up_votes', verbose_name='نظر آموزش')

    score = models.PositiveIntegerField(verbose_name='امتیاز')

    coin = models.PositiveIntegerField(verbose_name='سکه')


class TutorialCommentDownVote(models.Model):
    """ TutorialCommentDownVote model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tutorial_comment_down_votes',
        verbose_name='کاربر')

    comment = models.ForeignKey(
        TutorialComment, on_delete=models.CASCADE,
        related_name='down_votes', verbose_name='نظر آموزش')

    score = models.IntegerField(verbose_name='امتیاز')

    coin = models.IntegerField(verbose_name='سکه')
