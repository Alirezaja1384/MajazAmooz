from datetime import timedelta
from django.db import models
from django.utils.text import slugify
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.core.exceptions import ValidationError
from django_resized import ResizedImageField
from django_bleach.models import BleachField
from shared.models import ConfirmStatusChoices


class Exam(models.Model):
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
        null=True,
        blank=True,
        verbose_name="مدت زمان تحویل",
        # deadline_duration must be at least 1 minute
        validators=[MinValueValidator(timedelta(minutes=1))],
    )
    waiting_duration = models.DurationField(
        null=True,
        blank=True,
        default=timedelta(minutes=1),
        verbose_name="زمان انتظار",
        help_text="زمان انتظار برای تحویل این آزمون پس از اتمام",
    )

    starts_at = models.DateTimeField(
        null=True, blank=True, verbose_name="زمان شروع"
    )
    ends_at = models.DateTimeField(
        null=True, blank=True, verbose_name="زمان پایان"
    )

    coin_cost = models.PositiveIntegerField(verbose_name="قیمت به سکه")
    diamond_cost = models.PositiveIntegerField(verbose_name="قیمت به الماس")

    correct_score = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1)],
        verbose_name="امتیاز جواب صحیح",
    )
    blank_score = models.IntegerField(
        default=0,
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
        editable=False,
        on_delete=models.CASCADE,
        related_name="exams",
        verbose_name="طراح آزمون",
    )

    categories = models.ManyToManyField(
        to="learning.Category",
        related_name="exams",
        verbose_name="دسته بندی ها",
    )

    participants = models.ManyToManyField(
        to="authentication.User",
        through="exam.ExamParticipation",
        related_name="participated_exams",
        verbose_name="شرکت کنندگان",
    )

    likers = models.ManyToManyField(
        "authentication.User",
        related_name="liked_exams",
        verbose_name="کاربران لایک کرده",
    )

    def clean(self):
        """Validates exam fields.

        Raises:
            ValidationError: When correct_score is NOT greater than
                blank_score.

            ValidationError: When blank_score is greater than or equal
                to incorrect_score.

            ValidationError: When ends_at is less than or equal starts_at.
        """
        if not (self.correct_score > self.blank_score):
            raise ValidationError(
                "امتیاز جواب صحیح باید بزرگتر از امتیاز نزده باشد"
            )

        if not (self.blank_score >= self.incorrect_score):
            raise ValidationError(
                "امتیاز نزده باید بزرگتر یا برابر از امتیاز جواب غلط باشد"
            )

        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError("زمان پایان باید بعد از زمان شروع باشد")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "آزمون"
        verbose_name_plural = "آزمون ها"
