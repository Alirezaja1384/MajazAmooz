""" Tutorial model """
from django.db import models

from authentication.models import User

from .category import Category


class Tutorial(models.Model):
    """ Tutorial model """
    CONFIRM_STATUS_CHOICES = [
        (-1, 'عدم تایید'),
        (0, 'در انتظار تایید'),
        (1, 'تایید شده'),
    ]

    title = models.CharField(max_length=30, verbose_name='عنوان')

    slug = models.SlugField(
        max_length=50, allow_unicode=True, verbose_name='اسلاگ')

    short_description = models.CharField(
        max_length=250, verbose_name='توضیح کوتاه')

    body = models.TextField(verbose_name='بدنه')

    total_views = models.PositiveIntegerField(verbose_name='بازدید کل')
    user_views = models.PositiveIntegerField(verbose_name='بازدید کاربران')

    up_votes = models.PositiveIntegerField(verbose_name='امتیاز مثبت')
    down_votes = models.PositiveIntegerField(verbose_name='امتیاز منفی')

    likes = models.PositiveIntegerField(verbose_name='لایک ها')

    image = models.ImageField(
        upload_to="images/tutorial_thumbnails", blank=True, verbose_name='تصویر')

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name='زمان انتشار')

    last_edit_date = models.DateField(
        auto_now=True, verbose_name='زمان آخرین ویرایش')

    confirm_status = models.IntegerField(
        choices=CONFIRM_STATUS_CHOICES, verbose_name='وضعیت تایید')

    is_edited = models.BooleanField(default=True, verbose_name='ویرایش شده')

    is_active = models.BooleanField(default=True, verbose_name='فعال')

    # Relations
    author = models.ForeignKey(
        User, related_name='tutorials', verbose_name='نویسنده')

    categories = models.ManyToManyField(
        Category, related_name='tutorials', verbose_name='دسته بندی ها')
