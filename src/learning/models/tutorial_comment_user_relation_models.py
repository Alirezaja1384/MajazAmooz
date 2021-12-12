"""
    TutorialComment-User many to many relation models
"""
from constance import config
from django.db import models
from shared.models import AbstractScoreCoinModel
from learning.querysets.tutorial_comment_user_relation_querysets import (
    TutorialCommentUserRelationQueryset,
)


class TutorialCommentLike(AbstractScoreCoinModel):
    """TutorialCommentLike model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_comment_likes",
        verbose_name="کاربر",
    )

    comment = models.ForeignKey(
        to="learning.TutorialComment",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="نظر آموزش",
    )

    # AbstractScoreCoinModel's settings
    user_relation_field = "comment.user"
    object_relation_field = "comment"
    object_relation_count_field_name = "likes_count"

    # Custom queryset
    objects = TutorialCommentUserRelationQueryset.as_manager()

    def get_create_score(self):
        return config.TUTORIAL_COMMENT_LIKE_SCORE

    def get_create_coin(self):
        return config.TUTORIAL_COMMENT_LIKE_COIN


class TutorialCommentUpVote(AbstractScoreCoinModel):
    """TutorialCommentUpVote model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_comment_up_votes",
        verbose_name="کاربر",
    )

    comment = models.ForeignKey(
        to="learning.TutorialComment",
        on_delete=models.CASCADE,
        related_name="up_votes",
        verbose_name="نظر آموزش",
    )

    # Custom queryset
    objects = TutorialCommentUserRelationQueryset.as_manager()

    def get_create_score(self):
        return config.TUTORIAL_COMMENT_UPVOTE_SCORE

    def get_create_coin(self):
        return config.TUTORIAL_COMMENT_UPVOTE_COIN

    # AbstractScoreCoinModel's settings
    user_relation_field = "comment.user"
    object_relation_field = "comment"
    object_relation_count_field_name = "up_votes_count"


class TutorialCommentDownVote(AbstractScoreCoinModel):
    """TutorialCommentDownVote model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_comment_down_votes",
        verbose_name="کاربر",
    )

    comment = models.ForeignKey(
        to="learning.TutorialComment",
        on_delete=models.CASCADE,
        related_name="down_votes",
        verbose_name="نظر آموزش",
    )

    # Custom queryset
    objects = TutorialCommentUserRelationQueryset.as_manager()

    def get_create_score(self):
        return config.TUTORIAL_COMMENT_DOWNVOTE_SCORE

    def get_create_coin(self):
        return config.TUTORIAL_COMMENT_DOWNVOTE_COIN

    # AbstractScoreCoinModel's settings
    user_relation_field = "comment.user"
    object_relation_field = "comment"
    object_relation_count_field_name = "down_votes_count"
