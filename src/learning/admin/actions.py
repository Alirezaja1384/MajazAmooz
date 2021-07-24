from django.http import HttpRequest
from django.contrib import admin, messages
from django.contrib.admin import ModelAdmin
from django.db.models import QuerySet
from shared.models import ConfirmStatusChoices
from learning.notifications import (
    NotificationResult,
    TutorialConfirmDisproveNotifier,
    TutorialCommentConfirmDisproveNotifier,
    TutorialCommentReplyNotifier,
    TutorialAuthorNewConfirmedCommentNotifier,
)
from learning.models import TutorialComment


def message_user_email_results(
    request: HttpRequest,
    modeladmin: ModelAdmin,
    notifications_result: NotificationResult,
):

    if notifications_result.success:
        successful_notifications_msg = (
            f"{notifications_result.success} اطلاعیه با موفقیت ارسال شد"
        )
        modeladmin.message_user(
            request, successful_notifications_msg, messages.SUCCESS
        )

    if notifications_result.failed:
        failed_notifications_msg = (
            f"ارسال {notifications_result.failed} اطلاعیه با خطا مواجه شد"
        )
        modeladmin.message_user(
            request, failed_notifications_msg, messages.ERROR
        )


@admin.action(
    permissions=["confirm_disprove"], description="تایید آموزش های انتخاب شده"
)
def confirm_tutorial_action(
    modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet
):

    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.CONFIRMED
    ).filter(is_active=True)
    update_item_pks = [tutorial.pk for tutorial in update_queryset]

    updated = update_queryset.update(
        confirm_status=ConfirmStatusChoices.CONFIRMED
    )

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks
    ).select_related("author")

    # Send notifications
    notifier = TutorialConfirmDisproveNotifier(request, send_mail_queryset)
    notify_result = notifier.notify()

    # Send messages
    modeladmin.message_user(
        request, f"{updated} مورد با موفقیت تایید شد", messages.SUCCESS
    )

    message_user_email_results(request, modeladmin, notify_result)


@admin.action(
    permissions=["confirm_disprove"], description="رد آموزش های انتخاب شده"
)
def disprove_tutorial_action(
    modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet
):

    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.DISPROVED
    ).filter(is_active=True)
    update_item_pks = [tutorial.pk for tutorial in update_queryset]

    updated = update_queryset.update(
        confirm_status=ConfirmStatusChoices.DISPROVED
    )

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks
    ).select_related("author")

    # Send notifications
    notifier = TutorialConfirmDisproveNotifier(request, send_mail_queryset)
    notify_result = notifier.notify()

    modeladmin.message_user(
        request, f"{updated} مورد با موفقیت رد شد", messages.SUCCESS
    )

    message_user_email_results(request, modeladmin, notify_result)


@admin.action(
    permissions=["confirm_disprove"], description="تایید دیدگاه های انتخاب شده"
)
def confirm_tutorial_comment_action(
    modeladmin: ModelAdmin,
    request: HttpRequest,
    queryset: QuerySet[TutorialComment],
):

    # After update update_queryset becomes empty because of applied exclusion
    # then we store update item primary keys in update_item_pks t use later
    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.CONFIRMED
    ).filter(is_active=True)
    update_item_pks = [comment.pk for comment in update_queryset]

    updated_count = update_queryset.update(
        confirm_status=ConfirmStatusChoices.CONFIRMED
    )

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks
    ).select_related(
        "user", "tutorial", "parent_comment", "parent_comment__user"
    )

    # Send notifications
    confirm_disprove_notifier_result = TutorialCommentConfirmDisproveNotifier(
        request, send_mail_queryset
    ).notify()

    reply_notifier_result = TutorialCommentReplyNotifier(
        request, send_mail_queryset
    ).notify()

    tutorial_author_new_comment_notifier_result = (
        TutorialAuthorNewConfirmedCommentNotifier(
            request, send_mail_queryset
        ).notify()
    )

    emails_result = (
        confirm_disprove_notifier_result
        + reply_notifier_result
        + tutorial_author_new_comment_notifier_result
    )

    # Send messages
    confirm_msg = f"{updated_count} مورد با موفقیت تایید شد"
    modeladmin.message_user(request, confirm_msg, messages.SUCCESS)
    message_user_email_results(request, modeladmin, emails_result)


@admin.action(
    permissions=["confirm_disprove"], description="رد دیدگاه های انتخاب شده"
)
def disprove_tutorial_comment_action(
    modeladmin: ModelAdmin, request: HttpRequest, queryset: QuerySet
):

    # After update update_queryset becomes empty because of applied exclusion
    # thus, we store update item primary keys in update_item_pks t use later
    update_queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.DISPROVED
    ).filter(is_active=True)
    update_item_pks = [comment.pk for comment in update_queryset]

    updated_count = update_queryset.update(
        confirm_status=ConfirmStatusChoices.DISPROVED
    )

    # Execute new query to get updated objects for notification
    send_mail_queryset = queryset.filter(
        pk__in=update_item_pks
    ).select_related("user", "tutorial")

    # Send notifications
    confirm_disprove_notifier_result = TutorialCommentConfirmDisproveNotifier(
        request, send_mail_queryset
    ).notify()

    modeladmin.message_user(
        request, f"{updated_count} مورد با موفقیت رد شد", messages.SUCCESS
    )

    message_user_email_results(
        request, modeladmin, confirm_disprove_notifier_result
    )
