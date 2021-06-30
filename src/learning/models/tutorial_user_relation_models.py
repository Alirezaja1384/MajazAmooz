"""
    Tutorial-User many to many relation models
"""
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django_lifecycle import hook, AFTER_CREATE, BEFORE_DELETE
from learning.models import Tutorial
from learning.querysets import TutorialUserRelationQueryset
from authentication.models import User
from shared.models import AbstractScoreCoinModel


class AbstractTutorialScoreCoinModel(AbstractScoreCoinModel):
    """Abstract tutorial score-coin model

    Needs these (required ones flagged by *):
        [tutorial relation field *]: required for increase/decrease
                                     object's count and author's score and coin

        [tutorial_object_count_field]: object field on tutorial model to
            increase/decrease on insert/delete. Defaults to None.

    Provides these hooks:
        AFTER_CREATE: increases author's score and coin by object's
            score and coin field and object count for tutorial model
            (if specified by tutorial_object_count_field)

        AFTER_CREATE: decreases author's score and coin by object's
            score andcoin field and object count on tutorial model
            (if specified by tutorial_object_count_field)
    """

    tutorial_object_count_field = None

    @property
    def tutorial(self):
        msg = "You should implement tutorial field to use \
            AbstractTutorialScoreCoinModel"
        raise ImproperlyConfigured(msg)

    @hook(AFTER_CREATE)
    def on_create(self):
        # Increase author's scores and coins
        self.tutorial.author.scores += self.score
        self.tutorial.author.coins += self.coin
        self.tutorial.author.save(update_fields=["scores", "coins"])

        if self.tutorial_object_count_field:
            # Increase tutorial.{tutorial_object_count_field}
            current_count = getattr(
                self.tutorial, self.tutorial_object_count_field
            )
            setattr(
                self.tutorial,
                self.tutorial_object_count_field,
                current_count + 1,
            )
            self.tutorial.save(
                update_fields=[self.tutorial_object_count_field]
            )

    @hook(BEFORE_DELETE)
    def on_delete(self):
        # Decrease author's scores and coins
        self.tutorial.author.scores -= self.score
        self.tutorial.author.coins -= self.coin
        self.tutorial.author.save(update_fields=["scores", "coins"])

        if self.tutorial_object_count_field:
            # Increase tutorial.{tutorial_object_count_field}
            current_count = getattr(
                self.tutorial, self.tutorial_object_count_field
            )
            setattr(
                self.tutorial,
                self.tutorial_object_count_field,
                current_count - 1,
            )
            self.tutorial.save(
                update_fields=[self.tutorial_object_count_field]
            )

    objects = TutorialUserRelationQueryset.as_manager()

    class Meta:
        abstract = True


class TutorialView(AbstractTutorialScoreCoinModel):
    """TutorialView model"""

    tutorial_object_count_field = "user_views_count"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tutorial_views",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        Tutorial,
        on_delete=models.CASCADE,
        related_name="views",
        verbose_name="آموزش",
    )


class TutorialLike(AbstractTutorialScoreCoinModel):
    """TutorialLike model"""

    tutorial_object_count_field = "likes_count"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tutorial_likes",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        Tutorial,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="آموزش",
    )


class TutorialUpVote(AbstractTutorialScoreCoinModel):
    """TutorialUpVote model"""

    tutorial_object_count_field = "up_votes_count"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tutorial_up_votes",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        Tutorial,
        on_delete=models.CASCADE,
        related_name="up_votes",
        verbose_name="آموزش",
    )


class TutorialDownVote(AbstractTutorialScoreCoinModel):
    """TutorialDownVote model"""

    tutorial_object_count_field = "down_votes_count"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tutorial_down_votes",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        Tutorial,
        on_delete=models.CASCADE,
        related_name="down_votes",
        verbose_name="آموزش",
    )
