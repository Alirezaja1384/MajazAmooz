"""
    Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    " Customized user model "

    avatar = models.ImageField(
        "تصویر پروفایل", upload_to="images/avatars", blank=True)

    scores = models.PositiveIntegerField("امتیاز", default=0)

    coins = models.PositiveIntegerField("سکه ها", default=0)

    diamonds = models.PositiveIntegerField("الماس ها", default=0)
