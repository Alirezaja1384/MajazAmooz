"""
    Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    " Customized user model "

    avatar = models.ImageField(
        "تصویر پروفایل", upload_to="images/avatars",
        default="default/authentication/user-avatar.png")

    scores = models.IntegerField("امتیاز", default=0)

    coins = models.IntegerField("سکه ها", default=0)

    diamonds = models.PositiveIntegerField("الماس ها", default=0)
