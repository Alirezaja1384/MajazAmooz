from django.http import HttpRequest
from django.contrib import (admin, messages)
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet

from utilities.model_utils import ConfirmStatusChoices
from learning.emails import notify_tutorial_comments_reply
from learning.models import TutorialComment


# TODO: Add permissions
@admin.action(description='تایید دیدگاه های انتخاب شده')
def confirm_tutorial_comment_action(modeladmin: ModelAdmin, request: HttpRequest,
                                    queryset: QuerySet[TutorialComment]):

    queryset = queryset.exclude(confirm_status=ConfirmStatusChoices.CONFIRMED
                                ).filter(is_active=True)

    # Send email before update because after update queryset will be empty by exclusion
    email_success_count, email_failed_count = notify_tutorial_comments_reply(
        request, queryset)

    updated = queryset.update(confirm_status=ConfirmStatusChoices.CONFIRMED)

    confirm_msg = f"{updated} مورد با موفقیت تایید شد"
    modeladmin.message_user(request, confirm_msg, messages.SUCCESS)

    if email_success_count:
        successful_email_msg = f'{email_success_count} ایمیل با موفقیت ارسال شد'
        modeladmin.message_user(
            request, successful_email_msg, messages.SUCCESS)

    if email_failed_count:
        failed_email_msg = f'ارسال {email_failed_count} ایمیل با خطا مواجه شد'
        modeladmin.message_user(request, failed_email_msg, messages.ERROR)


@admin.action(description='رد دیدگاه های انتخاب شده')
def disprove_tutorial_comment_action(modeladmin: ModelAdmin, request: HttpRequest,
                                     queryset: QuerySet):

    updated = queryset.update(confirm_status=ConfirmStatusChoices.DISPROVED)

    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت رد شد",
                            messages.SUCCESS)


@admin.action(description='تایید آموزش های انتخاب شده')
def confirm_tutorial_action(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet):
    updated = queryset.update(confirm_status=ConfirmStatusChoices.DISPROVED)

    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت رد شد",
                            messages.SUCCESS)


@admin.action(description='رد آموزش های انتخاب شده')
def disprove_tutorial_action(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet):
    updated = queryset.update(confirm_status=ConfirmStatusChoices.DISPROVED)

    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت رد شد",
                            messages.SUCCESS)
