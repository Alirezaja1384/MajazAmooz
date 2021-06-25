"""
    TutorialComment-User many to many relation models
"""
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django_lifecycle import (
    hook, AFTER_CREATE, BEFORE_DELETE
)

from authentication.models import User
from learning.models import TutorialComment
from learning.querysets import TutorialCommentUserRelationQuerySet
from shared.models import AbstractScoreCoinModel


class AbstractCommentScoreCoinModel(AbstractScoreCoinModel):
    """ Abstract comment score-coin model

    Needs these (required ones flagged by *):
        [comment relation field *]: required for increase/decrease
                                     object's count and comment.user's score and coin

        [comment_object_count_field]: object field on comment model to increase/decrease
                                       on insert/delete. Defaults to None.

    Provides these hooks:
        AFTER_CREATE: increases comment.user's score and coin by object's
                      score and coin field and object count on
                      comment model (if specified by comment_object_count_field)

        AFTER_CREATE: decreases comment.user's score and coin by object's
                      score andcoin field and object count on
                      comment model (if specified by comment_object_count_field)
    """
    comment_object_count_field = None

    @property
    def comment(self):
        raise ImproperlyConfigured(
            'You should implement comment field to use AbstractCommentScoreCoinModel')

    @hook(AFTER_CREATE)
    def on_create(self):
        # Increase commnet.user's scores and coins
        self.comment.user.scores += self.score
        self.comment.user.coins += self.coin
        self.comment.user.save(update_fields=['scores', 'coins'])

        if self.comment_object_count_field:
            # Increase comment.{comment_object_count_field}
            current_count = getattr(
                self.comment, self.comment_object_count_field)
            setattr(self.comment, self.comment_object_count_field,
                    current_count + 1)
            self.comment.save(update_fields=[self.comment_object_count_field])

    @hook(BEFORE_DELETE)
    def on_delete(self):
        # Decrease commnet.user's scores and coins
        self.comment.user.scores -= self.score
        self.comment.user.coins -= self.coin
        self.comment.user.save(update_fields=['scores', 'coins'])

        if self.comment_object_count_field and self.comment:
            # Decrease comment.{comment_object_count_field}
            current_count = getattr(
                self.comment, self.comment_object_count_field)
            setattr(self.comment, self.comment_object_count_field,
                    current_count - 1)
            self.comment.save(update_fields=[self.comment_object_count_field])

    # Custom queryset
    objects = TutorialCommentUserRelationQuerySet.as_manager()

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
