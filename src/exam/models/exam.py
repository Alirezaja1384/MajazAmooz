from datetime import timedelta
from django.db import models
from django.utils.text import slugify
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django_resized import ResizedImageField
from django_bleach.models import BleachField
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE
from shared.models import ConfirmStatusChoices


class Exam(LifecycleModel):
    title = models.CharField(
        unique=True,
        max_length=255,
        verbose_name="عنوان",
    )
    slug = models.SlugField(
        max_length=255, allow_unicode=True, verbose_name="اسلاگ"
    )

    short_description = BleachField(max_length=255, verbose_name="توضیح کوتاه")
    full_description = BleachField(verbose_name="توضیح کامل")

    deadline_duration = models.DurationField(
        null=True, blank=True, verbose_name="مدت زمان تحویل"
    )
    waiting_duration = models.DurationField(
        null=True,
        blank=True,
        default=timedelta(minutes=1),
        verbose_name="زمان انتظار",
        help_text="زمان انتظار برای تحویل این آزمون پس از اتمام",
    )

    starts_at = models.DateTimeField(null=True, verbose_name="زمان شروع")
    ends_at = models.DateTimeField(null=True, verbose_name="زمان پایان")

    coin_cost = models.PositiveIntegerField(verbose_name="قیمت به سکه")
    diamond_cost = models.PositiveIntegerField(verbose_name="قیمت به الماس")

    correct_score = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        verbose_name="امتیاز جواب صحیح",
    )
    blank_score = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(1)],
        verbose_name="امتیاز نزده",
    )
    incorrect_score = models.IntegerField(
        default=-1,
        validators=[MaxValueValidator(0)],
        verbose_name="امتیاز جواب غلط",
    )

    correct_coin = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        verbose_name="سکه جواب صحیح",
    )

    image = ResizedImageField(
        upload_to="images/exam_thumbnails",
        default="default/exam/exam-image.png",
        size=[960, 540],
        crop=["middle", "center"],
        verbose_name="تصویر",
    )

    confirm_status = models.IntegerField(
        null=False,
        choices=ConfirmStatusChoices.choices,
        default=ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        verbose_name="وضعیت تایید",
    )

    views_count = models.PositiveIntegerField(
        verbose_name="تعداد بازدید", default=0
    )
    likes_count = models.PositiveIntegerField(
        verbose_name="تعداد لایک", default=0
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # Relations
    designer = models.ForeignKey(
        "authentication.User",
        null=False,
        on_delete=models.CASCADE,
        related_name="exams",
        verbose_name="طراح آزمون",
    )

    categories = models.ManyToManyField(
        to="learning.Category",
        related_name="exams",
        verbose_name="دسته بندی ها",
    )

    likers = models.ManyToManyField(
        "authentication.User",
        related_name="liked_exams",
        verbose_name="کاربران لایک کرده",
    )

    @hook(BEFORE_SAVE)
    def before_save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "آزمون"
        verbose_name_plural = "آزمون ها"
