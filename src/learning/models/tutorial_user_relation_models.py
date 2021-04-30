"""
    Tutorial-User many to many relation models
"""
from django.db import models

from authentication.models import User

from . import Tutorial


class TutorialView(models.Model):
    """ TutorialView model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='کاربر')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, verbose_name='آموزش')

    score = models.PositiveIntegerField(verbose_name='امتیاز')

    coin = models.PositiveIntegerField(verbose_name='سکه')


class TutorialLike(models.Model):
    """ TutorialLike model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='کاربر')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, verbose_name='آموزش')

    score = models.PositiveIntegerField(verbose_name='امتیاز')

    coin = models.PositiveIntegerField(verbose_name='سکه')


class TutorialUpVote(models.Model):
    """ TutorialUpVote model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='کاربر')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, verbose_name='آموزش')

    score = models.PositiveIntegerField(verbose_name='امتیاز')

    coin = models.PositiveIntegerField(verbose_name='سکه')


class TutorialDownVote(models.Model):
    """ TutorialDownVote model """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='کاربر')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, verbose_name='آموزش')

    score = models.IntegerField(verbose_name='امتیاز')

    coin = models.IntegerField(verbose_name='سکه')
