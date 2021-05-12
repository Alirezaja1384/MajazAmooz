"""
    TutorialComment-User many to many relation models
"""
from django.db import models

from django_lifecycle import (
    hook, AFTER_CREATE, BEFORE_DELETE
)

from authentication.models import User
from learning.models import TutorialComment
from utilities.models import AbstractScoreCoinModel


class AbstractCommentScoreCoinModel(AbstractScoreCoinModel):

    comment_object_count_field = None

    @property
    def comment(self):
        raise NotImplementedError

    @hook(AFTER_CREATE)
    def on_create(self):
        self.comment.user.scores += self.score
        self.comment.user.coins += self.coin
        self.comment.user.save()

        if self.comment_object_count_field :
            # Increase comment.{comment_object_count_field}
            current_count = getattr(self.comment, self.comment_object_count_field)
            setattr(self.comment, self.comment_object_count_field, current_count + 1)
            self.comment.save()

    @hook(BEFORE_DELETE)
    def on_delete(self):
        self.comment.user.scores -= self.score
        self.comment.user.coins -= self.coin
        self.comment.user.save()

        if self.comment_object_count_field and self.comment:
            # Decrease comment.{comment_object_count_field}
            current_count = getattr(self.comment, self.comment_object_count_field)
            setattr(self.comment, self.comment_object_count_field, current_count - 1)
            self.comment.save()

    class Meta:
        abstract = True


class TutorialCommentLike(AbstractCommentScoreCoinModel):
    """ TutorialCommentLike model """

    comment_object_count_field = 'likes_count'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tutorial_comment_likes', verbose_name='کاربر')

    comment = models.ForeignKey(
        TutorialComment, on_delete=models.CASCADE,
        related_name='likes', verbose_name='نظر آموزش')


class TutorialCommentUpVote(AbstractCommentScoreCoinModel):
    """ TutorialCommentUpVote model """

    comment_object_count_field = 'up_votes_count'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tutorial_comment_up_votes',
        verbose_name='کاربر')

    comment = models.ForeignKey(
        TutorialComment, on_delete=models.CASCADE,
        related_name='up_votes', verbose_name='نظر آموزش')


class TutorialCommentDownVote(AbstractCommentScoreCoinModel):
    """ TutorialCommentDownVote model """

    comment_object_count_field = 'down_votes_count'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='tutorial_comment_down_votes',
        verbose_name='کاربر')

    comment = models.ForeignKey(
        TutorialComment, on_delete=models.CASCADE,
        related_name='down_votes', verbose_name='نظر آموزش')
