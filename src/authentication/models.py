"""
    Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    " Customized user model "

    avatar = models.ImageField(
        "تصویر پروفایل", upload_to="images/avatars", blank=True)

    scores = models.PositiveIntegerField("امتیاز", null=True, blank=True)

    coins = models.PositiveIntegerField("سکه ها", null=True, blank=True)

    diamonds = models.PositiveIntegerField("الماس ها", null=True, blank=True)
