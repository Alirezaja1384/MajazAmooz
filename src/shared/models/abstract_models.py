from django.db import models
from django_lifecycle import LifecycleModel


class AbstractScoreCoinModel(LifecycleModel):
    """
    Abstract score-coin model for using in
    score-coin based models like upvote, like, etc.
    """

    score = models.IntegerField(verbose_name="امتیاز", default=0)
    coin = models.IntegerField(verbose_name="سکه", default=0)

    create_date = models.DateTimeField(
        auto_now_add=True, null=True, verbose_name="زمان ایجاد"
    )

    class Meta:
        abstract = True
