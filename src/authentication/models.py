"""
    Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    " Customized user model "

    avatar = models.ImageField("تصویر پروفایل", upload_to="images/avatars")

    scores = models.PositiveIntegerField("امتیاز")

    coins = models.PositiveIntegerField("سکه ها")

    diamonds = models.PositiveIntegerField("الماس ها")
