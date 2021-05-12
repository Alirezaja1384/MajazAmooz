from django.db import models
from django_lifecycle import LifecycleModel


class AbstractScoreCoinModel(LifecycleModel):

    score = models.IntegerField(verbose_name='امتیاز', default=0)
    coin = models.IntegerField(verbose_name='سکه', default=0)

    class Meta:
        abstract = True
