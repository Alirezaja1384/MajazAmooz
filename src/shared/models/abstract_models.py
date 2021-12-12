from enum import Enum
from typing import Optional
from django.db import models
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django_lifecycle import (
    LifecycleModel,
    BEFORE_CREATE,
    AFTER_CREATE,
    BEFORE_DELETE,
    hook,
)

USER_MODEL = get_user_model()


class AbstractScoreCoinModel(LifecycleModel):
    """Abstract score-coin related model

    Configuration options[OPTIONAL]:
        [user_relation_field(models.Model)]: Object relation to user's
            model. Required to increase/decrease user's score and coin
            on insert/delete. It supports nested object attributes
            (e.g. tutorial.author).

        [object_relation_field(models.Model)]: Object relation to the object
            that liked, up_voted, saved, ... . Required to increase/decrease
            this model's count in object_relation_field's model on
            insert/delete.

        [object_relation_count_field_name(str)]: This models's count field
            in object_relation_field's model to increase/decrease on
            insert/delete. Defaults to None.

    Provides these hooks:
        AFTER_CREATE: Increases user's scores and coins by object's score
            and coin field and object count in object_relation_field' model
            by 1.(if specified by object_relation_count_field_name)

        BEFORE_DELETE: Decreases user's scores and coins by object's score
            and coin field and object count in object_relation_field' model
            by 1.(if specified by object_relation_count_field_name)
    """

    class ActionRate(Enum):
        CREATE = 1
        DELETE = -1

    # AbstractScoreCoinModel's settings
    user_relation_field: str = None
    object_relation_field: str = None
    object_relation_count_field_name: Optional[str] = ""

    # Model fields
    score = models.IntegerField(
        verbose_name="امتیاز", editable=False, default=0
    )
    coin = models.IntegerField(verbose_name="سکه", editable=False, default=0)

    create_date = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="زمان ایجاد"
    )

    class Meta:
        abstract = True

    @hook(BEFORE_CREATE)
    def before_create(self):
        self.score = self.get_create_score()
        self.coin = self.get_create_coin()

    @hook(AFTER_CREATE)
    def after_create(self):
        # Increase user's scores and coins if specified
        self._manage_user_score_coin(action_rate=self.ActionRate.CREATE)
        # Increase object's count if specified
        self._manage_object_relation_count(action_rate=self.ActionRate.CREATE)

    @hook(BEFORE_DELETE)
    def before_delete(self):
        # Decrease user's scores and coins if specified
        self._manage_user_score_coin(action_rate=self.ActionRate.DELETE)
        # Decrease object's count if specified
        self._manage_object_relation_count(action_rate=self.ActionRate.DELETE)

    def _manage_user_score_coin(self, action_rate: ActionRate):
        """Manages user's score and coin in user_relation_field's model.

        Args:
            action (ActionRate): Action rate (1 or -1).
        """

        def _raise_invalid_user():
            raise ImproperlyConfigured(
                "user_relation_field's value ({}) is not valid."
                " Make sure the value is a string and the model"
                " has this field.".format(self.user_relation_field)
            )

        if self.user_relation_field:
            # Raise if user_relation_field is not a string
            if self.user_relation_field and not isinstance(
                self.user_relation_field, str
            ):
                _raise_invalid_user()

            try:
                last_target = self
                for attr in self.user_relation_field.split("."):
                    # Get next attribute from last target
                    last_target = getattr(last_target, attr)
            except AttributeError:
                _raise_invalid_user()

            # Check if last_target is an instance of USER_MODEL
            if isinstance(last_target, USER_MODEL):
                user = last_target
            # Raise if it's not
            else:
                _raise_invalid_user()

            # Increase/Decrease user scores and coins
            setattr(  # noqa
                user,
                "coins",
                F("coins") + (self.coin * action_rate.value),
            )

            setattr(  # noqa
                user,
                "scores",
                F("scores") + (self.score * action_rate.value),
            )

            # Update user's score and coin
            user.save(update_fields=["scores", "coins"])

            # Refresh user object from database
            user.refresh_from_db(fields=["scores", "coins"])

    def _manage_object_relation_count(self, action_rate: ActionRate):
        """Manages this model's count number in object_relation_field's model.

        Args:
            action (ActionRate): Action rate (1 or -1).
        """

        def _raise_invalid_object():
            raise ImproperlyConfigured(
                "object_relation_field's value ({}) is not valid."
                " {} doesn't have this attribute.".format(
                    self.object_relation_field,
                    self.__class__.__name__,
                )
            )

        def _raise_invalid_object_relation_count_field():
            raise ImproperlyConfigured(
                "object_relation_count_field_name's value ({}) is not valid."
                " object_relation_field doesn't have this field.".format(
                    self.object_relation_count_field_name
                )
            )

        if (
            self.object_relation_field
            and self.object_relation_count_field_name
        ):
            # Raise if object_relation_field is not a string
            if self.object_relation_field and not isinstance(
                self.object_relation_field, str
            ):
                _raise_invalid_object()
            # Raise if object_relation_count_field_name is not a string
            if self.object_relation_count_field_name and not isinstance(
                self.object_relation_count_field_name, str
            ):
                _raise_invalid_object_relation_count_field()

            obj: models.Model = getattr(self, self.object_relation_field, None)

            # Raise if model doesn't have object_relation_field
            if not obj:
                _raise_invalid_object()
            # Raise if obj doesn't have {object_relation_count_field_name}
            if not hasattr(obj, self.object_relation_count_field_name):
                _raise_invalid_object_relation_count_field()

            # Increase/Decrease object's relation count
            setattr(
                obj,
                self.object_relation_count_field_name,
                F(self.object_relation_count_field_name) + action_rate.value,
            )

            # Update object's relation count
            obj.save(update_fields=[self.object_relation_count_field_name])

            # Refresh object from database
            obj.refresh_from_db(fields=[self.object_relation_count_field_name])

    def get_create_score(self) -> int:
        """Returns score value for model object creation.

        Returns:
            int: Model's creation score.
        """
        return 0

    def get_create_coin(self) -> int:
        """Returns coin value for model object creation.

        Returns:
            int: Model's creation coin.
        """
        return 0
