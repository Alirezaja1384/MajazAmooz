"""
    Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    " Customized user model "

    email = models.EmailField(max_length=254, unique=True,
                              verbose_name='ایمیل')

    avatar = models.ImageField(
        "تصویر پروفایل", upload_to="images/avatars",
        default="default/authentication/user-avatar.png")

    scores = models.IntegerField("امتیاز", default=0)

    coins = models.IntegerField("سکه ها", default=0)

    diamonds = models.PositiveIntegerField("الماس ها", default=0)

    email_confirmed = models.BooleanField(
        verbose_name='تایید ایمیل', default=False)

    # Goals
    tutorials_count_goal = models.PositiveIntegerField(
        default=20, verbose_name='تعداد آموزش هدف')
    comments_count_goal = models.PositiveIntegerField(
        default=50, verbose_name='تعداد دیدگاه هدف')
    likes_count_goal = models.PositiveIntegerField(
        default=200, verbose_name='تعداد لایک هدف')
    views_count_goal = models.PositiveIntegerField(
        default=200, verbose_name='تعداد بازدید هدف')

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

        permissions = (
            ('email_confirmed', 'ایمیل تایید شده'),
        )
