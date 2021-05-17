from django.http import HttpRequest
from django.contrib import (admin, messages)
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet

from utilities.model_utils import ConfirmStatusChoices
from learning.emails import (
    EmailsResult,
    notify_tutorial_comments_reply,
    notify_tutorial_comment_confirm_disprove,
    notify_tutorial_confirm_disprove
)
from learning.models import TutorialComment


def message_user_email_results(request: HttpRequest, modeladmin: ModelAdmin,
                               emails_result: EmailsResult):

    if emails_result.success:
        successful_email_msg = f'{emails_result.success} ایمیل با موفقیت ارسال شد'
        modeladmin.message_user(
            request, successful_email_msg, messages.SUCCESS)

    if emails_result.failed:
        failed_email_msg = f'ارسال {emails_result.failed} ایمیل با خطا مواجه شد'
        modeladmin.message_user(request, failed_email_msg, messages.ERROR)


# TODO: Add permissions
@admin.action(description='تایید دیدگاه های انتخاب شده')
def confirm_tutorial_comment_action(modeladmin: ModelAdmin, request: HttpRequest,
                                    queryset: QuerySet[TutorialComment]):

    # After update update_queryset becomes empty because of applied exclusion
    # then we store update item primary keys in update_item_pks t use later
    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.CONFIRMED).filter(is_active=True)
    update_item_pks = [comment.pk for comment in update_queryset]

    updated_count = update_queryset.update(
        confirm_status=ConfirmStatusChoices.CONFIRMED)

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks).select_related(
            'user', 'tutorial', 'parent_comment', 'parent_comment__user')

    # Send mails
    confirm_email = notify_tutorial_comment_confirm_disprove(
        request, send_mail_queryset)

    reply_email = notify_tutorial_comments_reply(
        request, send_mail_queryset)

    emails_result = confirm_email + reply_email

    # Send messages
    confirm_msg = f"{updated_count} مورد با موفقیت تایید شد"
    modeladmin.message_user(request, confirm_msg, messages.SUCCESS)
    message_user_email_results(request, modeladmin, emails_result)


@admin.action(description='رد دیدگاه های انتخاب شده')
def disprove_tutorial_comment_action(modeladmin: ModelAdmin, request: HttpRequest,
                                     queryset: QuerySet):

    # After update update_queryset becomes empty because of applied exclusion
    # then we store update item primary keys in update_item_pks t use later
    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.DISPROVED).filter(is_active=True)
    update_item_pks = [comment.pk for comment in update_queryset]

    updated_count = update_queryset.update(
        confirm_status=ConfirmStatusChoices.DISPROVED)

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(pk__in=update_item_pks
                                         ).select_related('user', 'tutorial')

    # Send mails
    disprove_email = notify_tutorial_confirm_disprove(
        request, send_mail_queryset)

    modeladmin.message_user(request,
                            f"{updated_count} مورد با موفقیت رد شد",
                            messages.SUCCESS)

    message_user_email_results(request, modeladmin, disprove_email)


@admin.action(description='تایید آموزش های انتخاب شده')
def confirm_tutorial_action(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet):

    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.CONFIRMED).filter(is_active=True)
    update_item_pks = [tutorial.pk for tutorial in update_queryset]

    updated = update_queryset.update(
        confirm_status=ConfirmStatusChoices.CONFIRMED)

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks).select_related('author')

    # Send mails
    confirm_email = notify_tutorial_confirm_disprove(
        request, send_mail_queryset)

    # Send messages
    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت تایید شد",
                            messages.SUCCESS)

    message_user_email_results(request, modeladmin, confirm_email)


@admin.action(description='رد آموزش های انتخاب شده')
def disprove_tutorial_action(modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet):

    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.DISPROVED).filter(is_active=True)
    update_item_pks = [tutorial.pk for tutorial in update_queryset]

    updated = update_queryset.update(
        confirm_status=ConfirmStatusChoices.DISPROVED)

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks).select_related('author')

    # Send mails
    disprove_email = notify_tutorial_confirm_disprove(
        request, send_mail_queryset)

    modeladmin.message_user(request,
                            f"{updated} مورد با موفقیت رد شد",
                            messages.SUCCESS)

    message_user_email_results(request, modeladmin, disprove_email)
