""" Tutorial model """
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from authentication.models import User

from django_lifecycle import LifecycleModel, hook, BEFORE_UPDATE, BEFORE_SAVE

from . import Category
from ..querysets import TutorialQuerySet


class Tutorial(LifecycleModel):
    """ Tutorial model """
    CONFIRM_STATUS_CHOICES = [
        (0, 'در انتظار تایید'),
        (-1, 'عدم تایید'),
        (1, 'تایید شده'),
    ]

    title = models.CharField(max_length=30, unique=True, verbose_name='عنوان')

    slug = models.SlugField(max_length=50, allow_unicode=True,
                            unique=True, blank=True, verbose_name='اسلاگ')

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
        default='default/learning/tutorial-image.png',
        verbose_name='تصویر')

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name='زمان انتشار')

    last_edit_date = models.DateField(
        blank=True, null=True, verbose_name='زمان آخرین ویرایش')

    confirm_status = models.IntegerField(
        choices=CONFIRM_STATUS_CHOICES, default=0,
        null=False, blank=False, verbose_name='وضعیت تایید')

    is_edited = models.BooleanField(default=False, verbose_name='ویرایش شده')

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

    class Meta:
        verbose_name = 'آموزش'
        verbose_name_plural = 'آموزش ها'
        ordering = ('-create_date', )

    def __str__(self):
        return self.title

    @hook(BEFORE_UPDATE, when_any=['title', 'slug', 'short_description', 'body', 'image'], has_changed=True)
    def on_edit(self):
        self.is_edited = True
        self.last_edit_date = timezone.now()

    @hook(BEFORE_SAVE)
    def on_save(self):
        self.slug = slugify(self.title, allow_unicode=True)

    # Custom manager
    objects = TutorialQuerySet.as_manager()


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
