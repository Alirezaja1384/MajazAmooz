""" TutorialComment model """
from django.db import models
from django.utils import timezone
from django_lifecycle import hook, BEFORE_UPDATE, LifecycleModel

from authentication.models import User
from utilities.model_utils import ConfirmStatusChoices

from . import Tutorial
from ..querysets import TutorialCommentQueryset


class TutorialComment(LifecycleModel):
    """ TutorialComment model """

    title = models.CharField(max_length=30, verbose_name='عنوان')

    body = models.TextField(max_length=500, verbose_name='بدنه')

    up_votes_count = models.PositiveIntegerField(
        default=0, verbose_name='امتیاز مثبت')
    down_votes_count = models.PositiveIntegerField(
        default=0, verbose_name='امتیاز منفی')

    likes_count = models.PositiveIntegerField(
        default=0, verbose_name='لایک ها')

    create_date = models.DateTimeField(
        auto_now_add=True, verbose_name='زمان انتشار')

    last_edit_date = models.DateField(blank=True, null=True,
                                      verbose_name='زمان آخرین ویرایش')

    confirm_status = models.IntegerField(
        choices=ConfirmStatusChoices.choices, null=False, blank=False,
        default=ConfirmStatusChoices.WAITING_FOR_CONFIRM, verbose_name='وضعیت تایید')

    is_edited = models.BooleanField(default=False, verbose_name='ویرایش شده')

    allow_reply = models.BooleanField(default=True, verbose_name='امکان پاسخ')
    notify_replies = models.BooleanField(
        default=True, verbose_name='اطلاع رسانی پاسخ ها')

    is_active = models.BooleanField(default=True, verbose_name='فعال')

    # Relations
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='tutorial_comments', verbose_name='کاربر')

    tutorial = models.ForeignKey(
        Tutorial, on_delete=models.SET_NULL, null=True,
        related_name='comments', verbose_name='آموزش')

    parent_comment = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='child_comments', verbose_name='پاسخ به')

    likes = models.ManyToManyField(
        User, through='TutorialCommentLike', related_name='tutorial_comment_likes',
        verbose_name='لایک دیدگاه ها')

    up_votes = models.ManyToManyField(
        User, through='TutorialCommentUpVote',
        related_name='tutorial_comment_up_votes', verbose_name='امتیاز مثبت دیدگاه ها')

    down_votes = models.ManyToManyField(
        User, through='TutorialCommentDownVote',
        related_name='tutorial_comment_down_votes', verbose_name='امتیاز منفی دیدگاه ها')

    class Meta:
        verbose_name = 'دیدگاه آموزش'
        verbose_name_plural = 'دیدگاه آموزش ها'
        ordering = ('-create_date', )

    def __str__(self):
        return self.title

    @hook(BEFORE_UPDATE, when_any=['title', 'body'], has_changed=True)
    def on_edit(self):
        self.is_edited = True
        self.last_edit_date = timezone.now()
        self.confirm_status = ConfirmStatusChoices.WAITING_FOR_CONFIRM

    # Custom manager
    objects = TutorialCommentQueryset.as_manager()
