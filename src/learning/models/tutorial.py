""" Tutorial model """
from django.db import models

from authentication.models import User

from . import Category


class Tutorial(models.Model):
    """ Tutorial model """
    CONFIRM_STATUS_CHOICES = [
        (0, 'در انتظار تایید'),
        (-1, 'عدم تایید'),
        (1, 'تایید شده'),
    ]

    title = models.CharField(max_length=30, verbose_name='عنوان')

    slug = models.SlugField(
        max_length=50, allow_unicode=True, verbose_name='اسلاگ')

    short_description = models.TextField(
        max_length=250, verbose_name='توضیح کوتاه')

    body = models.TextField(verbose_name='بدنه')

    total_views_count = models.PositiveIntegerField(
        verbose_name='بازدید کل', default=0)
    user_views_count = models.PositiveIntegerField(
        verbose_name='بازدید کاربران', default=0)

    up_votes_count = models.PositiveIntegerField(
        verbose_name='امتیاز مثبت', default=0)
    down_votes_count = models.PositiveIntegerField(
        verbose_name='امتیاز منفی', default=0)

    likes_count = models.PositiveIntegerField(
        verbose_name='لایک ها', default=0)

    image = models.ImageField(
        upload_to="images/tutorial_thumbnails",
        blank=True, verbose_name='تصویر')

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name='زمان انتشار')

    last_edit_date = models.DateField(
        auto_now=True, verbose_name='زمان آخرین ویرایش')

    confirm_status = models.IntegerField(
        choices=CONFIRM_STATUS_CHOICES, default=0,
        null=False, blank=False, verbose_name='وضعیت تایید')

    is_edited = models.BooleanField(default=True, verbose_name='ویرایش شده')

    is_active = models.BooleanField(default=True, verbose_name='فعال')

    # Relations
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tutorials', verbose_name='نویسنده')

    categories = models.ManyToManyField(
        Category, related_name='tutorials', blank=True, verbose_name='دسته بندی ها')

    views = models.ManyToManyField(
        User, through='TutorialView', related_name='tutorial_views', verbose_name='بازدید ها')

    likes = models.ManyToManyField(
        User, through='TutorialLike', related_name='tutorial_likes', verbose_name='لایک ها')

    up_votes = models.ManyToManyField(
        User, through='TutorialUpVote',
        related_name='tutorial_up_votes', verbose_name='امتیاز های مثبت')

    down_votes = models.ManyToManyField(
        User, through='TutorialDownVote',
        related_name='tutorial_down_votes', verbose_name='امتیاز های منفی')

    comments = models.ManyToManyField(
        User, through='TutorialComment',
        related_name='tutorial_comments', verbose_name='نظرات')

    class Meta:
        verbose_name = 'آموزش'
        verbose_name_plural = 'آموزش ها'

    def __str__(self):
        return self.title


class TutorialTag(models.Model):
    """ TutorialTag model """
    title = models.CharField(max_length=20, verbose_name='عنوان')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.CASCADE, related_name='tags', verbose_name='آموزش')

    class Meta:
        verbose_name = 'کلیدواژه'
        verbose_name_plural = 'کلیدواژه ها'

    def __str__(self):
        return self.title
