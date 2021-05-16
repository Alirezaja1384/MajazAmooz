from smtplib import SMTPException
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import resolve_url
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models import QuerySet

from utilities.model_utils import ConfirmStatusChoices
from learning.models import TutorialComment


FROM_EMAIL = getattr(settings, 'EMAIL_FROM', None)


def notify_tutorial_comments_reply(
        request: HttpRequest, queryset: QuerySet[TutorialComment]) -> tuple[int, int]:
    """ Notifies user about replied comments by sending email

    Args:
        queryset (QuerySet[TutorialComment]): Comments to notify
            their parents about reply by email

    Returns:
        tuple[int, int]: First item is email_success_count
               and second item is email_failed_count
    """
    email_success_count = 0
    email_failed_count = 0

    def _send_confirmation_mail(child_comment: TutorialComment):

        parent_comment: TutorialComment = child_comment.parent_comment

        subject = f'پاسخ به نظر "{parent_comment.title}"'

        tutorial = parent_comment.tutorial
        url = request.build_absolute_uri(resolve_url('learning:tutorial', slug=tutorial.slug) +
                                         f'#comment-{parent_comment.pk}')

        plain_message = (f'پاسخی برای نظر "{parent_comment.title}" ثبت شده و اکنون تایید شد'
                         f'لینک پاسخ: {url}')

        html_message = render_to_string('mails/tutorial_comment_reply.html', {
            'child_comment': child_comment,
            'parent_comment': parent_comment,
            'tutorial': tutorial,
            'url': url
        })

        email = EmailMultiAlternatives(
            subject, plain_message, FROM_EMAIL, to=[parent_comment.user.email]
        )
        email.attach_alternative(html_message, "text/html")

        try:
            email.send()
            return True
        except SMTPException:
            return False

    # Comments to notify their parent comments' user
    comments_with_parent = queryset.exclude(parent_comment=None).filter(
        parent_comment__confirm_status=ConfirmStatusChoices.CONFIRMED,
        parent_comment__is_active=True, parent_comment__notify_replies=True
    ).select_related('parent_comment', 'parent_comment__user')

    for comment in comments_with_parent:
        result = _send_confirmation_mail(comment)
        if result:
            email_success_count += 1
        else:
            email_failed_count += 1

    return (email_success_count, email_failed_count)
