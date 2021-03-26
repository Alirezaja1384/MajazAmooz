"""
    Authentication models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    " Customized user model "

    avatar = models.ImageField("تصویر پروفایل", upload_to="Images/Avatars")

    scores = models.IntegerField("امتیاز")

    coins = models.IntegerField("سکه ها")

    diamonds = models.IntegerField("الماس ها")
