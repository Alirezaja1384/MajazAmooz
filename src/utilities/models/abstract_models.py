from django.db import models
from django_lifecycle import LifecycleModel


class AbstractScoreCoinModel(LifecycleModel):
    """
        Abstract score-coin model for using in 
        score-coin based models like upvote, like, etc.
    """
    score = models.IntegerField(verbose_name='امتیاز', default=0)
    coin = models.IntegerField(verbose_name='سکه', default=0)

    class Meta:
        abstract = True
