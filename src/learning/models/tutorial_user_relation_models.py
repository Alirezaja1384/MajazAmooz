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

    score = models.PositiveIntegerField(verbose_name='امتیاز')

    coin = models.PositiveIntegerField(verbose_name='سکه')


class TutorialComment(models.Model):
    """ TutorialComment model """
    CONFIRM_STATUS_CHOICES = [
        (-1, 'عدم تایید'),
        (0, 'در انتظار تایید'),
        (1, 'تایید شده'),
    ]

    title = models.CharField(max_length=30, verbose_name='عنوان')

    body = models.TextField(max_length=500, verbose_name='بدنه')

    up_votes = models.PositiveIntegerField(verbose_name='امتیاز مثبت')
    down_votes = models.PositiveIntegerField(verbose_name='امتیاز منفی')

    likes = models.PositiveIntegerField(verbose_name='لایک ها')

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name='زمان انتشار')

    last_edit_date = models.DateField(
        auto_now=True, verbose_name='زمان آخرین ویرایش')

    confirm_status = models.IntegerField(
        choices=CONFIRM_STATUS_CHOICES, verbose_name='وضعیت تایید')

    is_edited = models.BooleanField(default=True, verbose_name='ویرایش شده')

    allow_reply = models.BooleanField(default=True, verbose_name='امکان پاسخ')
    notify_replies = models.BooleanField(
        default=True, verbose_name='اطلاع رسانی پاسخ ها')

    is_active = models.BooleanField(default=True, verbose_name='فعال')

    # Relations
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, verbose_name='کاربر')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.SET_NULL, null=True, verbose_name='آموزش')

    parent_comment = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='child_comments', verbose_name='پاسخ به')