from smtplib import SMTPException
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import resolve_url
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import QuerySet

from utilities.model_utils import ConfirmStatusChoices
from learning.models import (TutorialComment, Tutorial)


FROM_EMAIL = getattr(settings, 'EMAIL_FROM', None)


class EmailsResult:
    def __init__(self, success: int, failed: int):
        self.success = success
        self.failed = failed

    def __add__(self, other):
        return EmailsResult(self.success + other.success, self.failed + other.failed)


def send_mail(subject, to: list[str], plain_message=None,
              template=None, context=None):

    email = EmailMultiAlternatives(
        subject, plain_message, FROM_EMAIL, to=to
    )

    if template:
        html_message = render_to_string(template, context)
        email.attach_alternative(html_message, "text/html")

    try:
        email.send()
        return True
    except SMTPException:
        return False


def notify_tutorial_comments_reply(
        request: HttpRequest, queryset: QuerySet[TutorialComment]) -> EmailsResult:
    """ Notifies user about replied comments by sending email

    Args:
        request (HttpRequest): Required for making absolute url
        queryset (QuerySet[TutorialComment]): Comments to notify
            their parents about reply by email

    Returns:
        EmailsResult: Count of successful and failed emails
    """
    success_count = 0
    failed_count = 0

    def _send_notification_mail(child_comment: QuerySet[TutorialComment]) -> bool:

        parent_comment: TutorialComment = child_comment.parent_comment
        tutorial: Tutorial = parent_comment.tutorial

        url = request.build_absolute_uri(resolve_url('learning:tutorial', slug=tutorial.slug) +
                                         f'#comment-{parent_comment.pk}')

        to = [parent_comment.user.email]
        subject = f'پاسخ به نظر "{parent_comment.title}"'
        plain_message = (f'پاسخی برای نظر "{parent_comment.title}" ثبت شده و اکنون تایید شد'
                         f'لینک پاسخ: {url}')
        template = 'mails/tutorial_comment_reply.html'
        context = {
            'child_comment': child_comment,
            'parent_comment': parent_comment,
            'tutorial': tutorial,
            'url': url
        }

        return send_mail(subject, to, plain_message, template, context)

    # Comments to notify their parent comments' user
    comments_with_parent = queryset.exclude(parent_comment=None).filter(
        parent_comment__confirm_status=ConfirmStatusChoices.CONFIRMED,
        parent_comment__is_active=True, parent_comment__notify_replies=True
    ).select_related('parent_comment', 'parent_comment__user')

    for comment in comments_with_parent:
        result = _send_notification_mail(comment)
        if result:
            success_count += 1
        else:
            failed_count += 1

    return EmailsResult(success_count, failed_count)


def notify_tutorial_comment_confirm_disprove(
        request: HttpRequest, queryset: QuerySet[TutorialComment]) -> EmailsResult:
    """ Notifies user about comment confirmation/disprovation by email

    Args:
        request (HttpRequest): Required for making absolute url
        queryset (QuerySet[TutorialComment]): Queryset of confirmed/disproved comments

    Returns:
        EmailsResult: Count of successful and failed emails
    """
    success_count = 0
    failed_count = 0

    queryset = queryset.exclude(
        confirm_status=ConfirmStatusChoices.WAITING_FOR_CONFIRM)

    def _send_notification_mail(comment: TutorialComment) -> bool:
        tutorial = comment.tutorial

        if comment.confirm_status == ConfirmStatusChoices.CONFIRMED:
            status_text = 'تایید شد'
        else:
            status_text = 'رد شد'

        to = [comment.user.email]
        subject = f'دیدگاه "{comment.title}" {status_text}'
        plain_message = f'دیدگاه "{comment.title}" برای آموزش {tutorial.title} {status_text}'
        template = 'mails/tutorial_comment_confirm_disprove.html'
        context = {
            'status_text': status_text,
            'tutorial': tutorial,
            'comment': comment
        }

        if comment.confirm_status == ConfirmStatusChoices.CONFIRMED:

            url = request.build_absolute_uri(resolve_url(
                'learning:tutorial', slug=tutorial.slug) + f'#comment-{comment.pk}')

            plain_message += f'\n لینک پاسخ: {url}'
            context['url'] = url

        return send_mail(subject, to, plain_message, template, context)

    for comment in queryset:
        result = _send_notification_mail(comment)
        if result:
            success_count += 1
        else:
            failed_count += 1

    return EmailsResult(success_count, failed_count)
