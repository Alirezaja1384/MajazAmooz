from django.db import models
from django_lifecycle import LifecycleModel, BEFORE_CREATE, hook


class AbstractScoreCoinModel(LifecycleModel):
    """
    Abstract score-coin model for using in
    score-coin based models like upvote, like, etc.
    """

    score = models.IntegerField(
        verbose_name="امتیاز", editable=False, default=0
    )
    coin = models.IntegerField(verbose_name="سکه", editable=False, default=0)

    create_date = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="زمان ایجاد"
    )

    class Meta:
        abstract = True

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

    @hook(BEFORE_CREATE)
    def before_create(self):
        self.score = self.get_create_score()
        self.coin = self.get_create_coin()
