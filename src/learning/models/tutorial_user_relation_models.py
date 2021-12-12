"""
    Tutorial-User many to many relation models
"""
from constance import config
from django.db import models
from shared.models import AbstractScoreCoinModel
from learning.querysets.tutorial_user_relation_querysets import (
    TutorialUserRelationQueryset,
)


class TutorialView(AbstractScoreCoinModel):
    """TutorialView model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_views",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        to="learning.Tutorial",
        on_delete=models.CASCADE,
        related_name="views",
        verbose_name="آموزش",
    )

    # AbstractScoreCoinModel's settings
    user_relation_field = "user"
    object_relation_field = "tutorial"
    object_relation_count_field_name = "user_views_count"

    # Custom queryset
    objects = TutorialUserRelationQueryset.as_manager()

    def get_create_score(self) -> int:
        return config.TUTORIAL_VIEW_SCORE

    def get_create_coin(self) -> int:
        return config.TUTORIAL_VIEW_COIN


class TutorialLike(AbstractScoreCoinModel):
    """TutorialLike model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_likes",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        to="learning.Tutorial",
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="آموزش",
    )

    # AbstractScoreCoinModel's settings
    user_relation_field = "tutorial.author"
    object_relation_field = "tutorial"
    object_relation_count_field_name = "likes_count"

    # Custom queryset
    objects = TutorialUserRelationQueryset.as_manager()

    def get_create_score(self) -> int:
        return config.TUTORIAL_LIKE_SCORE

    def get_create_coin(self) -> int:
        return config.TUTORIAL_LIKE_COIN


class TutorialUpVote(AbstractScoreCoinModel):
    """TutorialUpVote model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_up_votes",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        to="learning.Tutorial",
        on_delete=models.CASCADE,
        related_name="up_votes",
        verbose_name="آموزش",
    )

    # Custom queryset
    objects = TutorialUserRelationQueryset.as_manager()

    # AbstractScoreCoinModel's settings
    user_relation_field = "tutorial.author"
    object_relation_field = "tutorial"
    object_relation_count_field_name = "up_votes_count"

    def get_create_score(self) -> int:
        return config.TUTORIAL_UPVOTE_SCORE

    def get_create_coin(self) -> int:
        return config.TUTORIAL_UPVOTE_COIN


class TutorialDownVote(AbstractScoreCoinModel):
    """TutorialDownVote model"""

    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        related_name="tutorial_down_votes",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        to="learning.Tutorial",
        on_delete=models.CASCADE,
        related_name="down_votes",
        verbose_name="آموزش",
    )

    # Custom queryset
    objects = TutorialUserRelationQueryset.as_manager()

    # AbstractScoreCoinModel's settings
    user_relation_field = "tutorial.author"
    object_relation_field = "tutorial"
    object_relation_count_field_name = "down_votes_count"

    def get_create_score(self) -> int:
        return config.TUTORIAL_DOWNVOTE_SCORE

    def get_create_coin(self) -> int:
        return config.TUTORIAL_DOWNVOTE_COIN
