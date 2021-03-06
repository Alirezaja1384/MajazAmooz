""" TutorialComment model """
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_lifecycle import hook, LifecycleModel, BEFORE_UPDATE, BEFORE_SAVE
from shared.models import BleachField
from shared.models import ConfirmStatusChoices
from learning.querysets.tutorial_comment_queryset import (
    TutorialCommentQueryset,
)


class TutorialComment(LifecycleModel):
    """TutorialComment model"""

    title = models.CharField(max_length=30, verbose_name="عنوان")

    body = BleachField(max_length=500, verbose_name="بدنه")

    up_votes_count = models.PositiveIntegerField(
        default=0, verbose_name="امتیاز مثبت"
    )
    down_votes_count = models.PositiveIntegerField(
        default=0, verbose_name="امتیاز منفی"
    )

    likes_count = models.PositiveIntegerField(
        default=0, verbose_name="لایک ها"
    )

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name="زمان انتشار"
    )

    last_edit_date = models.DateTimeField(
        blank=True, null=True, verbose_name="زمان آخرین ویرایش"
    )

    confirm_status = models.IntegerField(
        choices=ConfirmStatusChoices.choices,
        null=False,
        blank=False,
        default=ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        verbose_name="وضعیت تایید",
    )

    is_edited = models.BooleanField(default=False, verbose_name="ویرایش شده")

    allow_reply = models.BooleanField(default=True, verbose_name="امکان پاسخ")
    notify_replies = models.BooleanField(
        default=True, verbose_name="اطلاع رسانی پاسخ ها"
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # Relations
    user = models.ForeignKey(
        to="authentication.User",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="tutorial_comments",
        verbose_name="کاربر",
    )

    tutorial = models.ForeignKey(
        to="learning.Tutorial",
        on_delete=models.CASCADE,
        null=True,
        blank=False,
        related_name="comments",
        verbose_name="آموزش",
    )

    parent_comment = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_comments",
        verbose_name="پاسخ به",
    )

    likers = models.ManyToManyField(
        to="authentication.User",
        through="TutorialCommentLike",
        related_name="liked_tutorial_comments",
        verbose_name="لایک دیدگاه ها",
    )

    up_voters = models.ManyToManyField(
        to="authentication.User",
        through="TutorialCommentUpVote",
        related_name="up_voted_tutorial_comments",
        verbose_name="امتیاز مثبت دیدگاه ها",
    )

    down_voters = models.ManyToManyField(
        to="authentication.User",
        through="TutorialCommentDownVote",
        related_name="down_voted_tutorial_commens",
        verbose_name="امتیاز منفی دیدگاه ها",
    )

    # Lifecycle hooks
    @hook(BEFORE_UPDATE, when_any=["title", "body"], has_changed=True)
    def on_edit(self):
        self.is_edited = True
        self.last_edit_date = timezone.now()
        self.confirm_status = ConfirmStatusChoices.WAITING_FOR_CONFIRM

    @hook(BEFORE_SAVE)
    def on_save(self):
        if self.parent_comment:
            self.tutorial = self.parent_comment.tutorial

    # Validate data (for admin panel)
    def clean(self):
        if self.pk and self.pk == self.parent_comment_id:
            raise ValidationError("پاسخ نمی تواند با دیدگاه یکسان باشد")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "دیدگاه آموزش"
        verbose_name_plural = "دیدگاه آموزش ها"
        ordering = ("-create_date",)
        permissions = (("confirm_disprove_tutorialcomment", "تایید/رد نظرات"),)

    # Custom manager
    objects: TutorialCommentQueryset = TutorialCommentQueryset.as_manager()
