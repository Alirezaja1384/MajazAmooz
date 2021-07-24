import logging
from abc import ABC
from typing import Optional, Dict
from smtplib import SMTPException
from django.db.models import Model
from django.http import HttpRequest
from django.shortcuts import resolve_url
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet, Q
from shared.models import ConfirmStatusChoices
from learning.models import TutorialComment, Tutorial


logger = logging.getLogger("emails")


class NotificationResult:
    def __init__(self, success: int = 0, failed: int = 0):
        self.success = success
        self.failed = failed

    def __add__(self, other):
        return NotificationResult(
            self.success + other.success, self.failed + other.failed
        )


class AbstractQuerysetNotifier(ABC):
    def __init__(self, request: HttpRequest, queryset: QuerySet):
        self.request = request
        self.queryset = queryset

    def get_queryset(self) -> QuerySet:
        """Returns queryset to notify about its objects.

        Returns:
            QuerySet: Notification objects queryset.
        """
        return self.queryset

    def notify(self) -> NotificationResult:
        """Notifies about queryset objects

        Returns:
            NotificationResult: Count of succeeded and failed notifications.
        """
        notification_email_result = NotificationResult()

        for obj in self.get_queryset():
            # Notify by email
            email_result = self.notify_by_email(obj, self.build_url(obj))
            if email_result:
                notification_email_result.success += 1
            else:
                notification_email_result.failed += 1

        return notification_email_result

    def notify_by_email(self, obj: Model, url: Optional[str] = None) -> bool:
        """Notifies about given object by email.

        Args:
            obj (Model): Model object to notify about it.
            url (Optional[str], optional): Notification url.
                Defaults to None.

        Raises:
            ImproperlyConfigured: It should be implemented by user. otherwise,
                it will raise ImproperlyConfigured.

        Returns:
            bool: True if sending email was successful. otherwise,
                returns False.
        """
        raise ImproperlyConfigured(
            "notify_by_email has not been configured yet."
        )

    def build_url(self, obj: Model) -> str:
        """Builds url for given object.

        Args:
            object (Model): Model object to build url.

        Returns:
            str: Generated url.
        """
        return None

    @staticmethod
    def send_email(
        subject: str,
        to_emails: list[str],
        plain_message: Optional[str] = None,
        template: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> bool:
        """Send email to given to_emails.

        Args:
            subject (str): Email subject.
            to_emails (list[str]): Sends emails to these emails.
            plain_message (Optional[str], optional): Email plain_message.
                Defaults to None.
            template (Optional[str], optional): Email template.
                Defaults to None.
            context (Optional[Dict], optional): Email template's context.
                Defaults to None.

        Returns:
            bool: True if sending was successful, otherwise False.
        """
        email = EmailMultiAlternatives(subject, plain_message, to=to_emails)

        if template:
            html_message = render_to_string(template, context)
            email.attach_alternative(html_message, "text/html")

        try:
            email.send()
            return True
        except SMTPException as ex:
            logger.warning(ex)
            return False


class TutorialConfirmDisproveNotifier(AbstractQuerysetNotifier):
    def get_queryset(self) -> QuerySet[Tutorial]:
        return self.queryset.exclude(
            confirm_status=ConfirmStatusChoices.WAITING_FOR_CONFIRM
        )

    def notify_by_email(
        self, obj: Tutorial, url: Optional[str] = None
    ) -> bool:
        template = "mails/tutorial_confirm_disprove.html"
        if obj.confirm_status == ConfirmStatusChoices.CONFIRMED:
            status_text = "تایید شد"
        else:
            status_text = "رد شد"

        to_emails = [obj.author.email]
        subject = "تایید/رد آموزش"
        plain_message = f'دیدگاه "{obj.title}" {status_text}'
        context = {
            "subject": subject,
            "status_text": status_text,
            "tutorial": obj,
        }

        if obj.confirm_status == ConfirmStatusChoices.CONFIRMED:
            plain_message += f"\n لینک آموزش: {url}"
            context["url"] = url

        return self.send_email(
            subject, to_emails, plain_message, template, context
        )

    def build_url(self, obj: Tutorial):
        return self.request.build_absolute_uri(
            resolve_url("learning:tutorial", slug=obj.slug)
        )


class TutorialCommentConfirmDisproveNotifier(AbstractQuerysetNotifier):
    def get_queryset(self) -> QuerySet[TutorialComment]:
        return self.queryset.exclude(
            Q(user=None)
            | Q(tutorial=None)
            | Q(confirm_status=ConfirmStatusChoices.WAITING_FOR_CONFIRM)
        )

    def notify_by_email(
        self, obj: TutorialComment, url: Optional[str] = None
    ) -> bool:
        template = "mails/tutorial_comment_confirm_disprove.html"
        tutorial = obj.tutorial

        if obj.confirm_status == ConfirmStatusChoices.CONFIRMED:
            status_text = "تایید شد"
        else:
            status_text = "رد شد"

        to_emails = [obj.user.email]
        subject = "تایید/رد دیدگاه"
        plain_message = (
            f'دیدگاه "{obj.title}" برای آموزش '
            f"{tutorial.title} {status_text}"
        )
        context = {
            "subject": subject,
            "status_text": status_text,
            "tutorial": tutorial,
            "comment": obj,
        }

        if obj.confirm_status == ConfirmStatusChoices.CONFIRMED:
            plain_message += f"\n لینک پاسخ: {url}"
            context["url"] = url

        return self.send_email(
            subject, to_emails, plain_message, template, context
        )

    def build_url(self, obj: TutorialComment):
        return self.request.build_absolute_uri(
            resolve_url("learning:tutorial", slug=obj.tutorial.slug)
            + f"#comment-{obj.pk}"
        )


class TutorialAuthorNewConfirmedCommentNotifier(AbstractQuerysetNotifier):
    def get_queryset(self) -> QuerySet[TutorialComment]:
        return self.queryset.exclude(
            Q(tutorial=None) | Q(tutorial__author=None)
        ).filter(
            confirm_status=ConfirmStatusChoices.CONFIRMED,
            is_active=True,
            tutorial__confirm_status=ConfirmStatusChoices.CONFIRMED,
            tutorial__is_active=True,
        )

    def notify_by_email(
        self, obj: TutorialComment, url: Optional[str] = None
    ) -> bool:
        template = "mails/tutorial_new_confirmed_comment.html"
        tutorial = obj.tutorial

        to_emails = [obj.tutorial.author.email]
        subject = "ثبت دیدگاه جدید برای آموزش شما"
        plain_message = (
            f'دیدگاه "{obj.title}" برای آموزش '
            f'"{tutorial.title}" ثبت و تایید شد \n'
            f"لینک دیدگاه: {url}"
        )
        context = {
            "subject": subject,
            "comment": obj,
            "tutorial": tutorial,
            "url": url,
        }

        return self.send_email(
            subject, to_emails, plain_message, template, context
        )

    def build_url(self, obj: TutorialComment):
        return self.request.build_absolute_uri(
            resolve_url("learning:tutorial", slug=obj.tutorial.slug)
            + f"#comment-{obj.pk}"
        )


class TutorialCommentReplyNotifier(AbstractQuerysetNotifier):
    def get_queryset(self) -> QuerySet[TutorialComment]:
        return (
            self.queryset.exclude(parent_comment=None)
            .filter(
                parent_comment__confirm_status=ConfirmStatusChoices.CONFIRMED,
                parent_comment__is_active=True,
                parent_comment__notify_replies=True,
            )
            .select_related("parent_comment", "parent_comment__user")
        )

    def notify_by_email(
        self, obj: TutorialComment, url: Optional[str] = None
    ) -> bool:
        template = "mails/tutorial_comment_reply.html"
        parent_comment: TutorialComment = obj.parent_comment
        tutorial: Tutorial = parent_comment.tutorial

        to_emails = [parent_comment.user.email]
        subject = f'پاسخ به نظر "{parent_comment.title}"'
        plain_message = (
            f'پاسخی برای نظر "{parent_comment.title}" ثبت شده و اکنون تایید شد'
            f"لینک پاسخ: {url}"
        )
        context = {
            "subject": subject,
            "child_comment": obj,
            "parent_comment": parent_comment,
            "tutorial": tutorial,
            "url": url,
        }

        return self.send_email(
            subject, to_emails, plain_message, template, context
        )

    def build_url(self, obj: TutorialComment):
        return self.request.build_absolute_uri(
            resolve_url("learning:tutorial", slug=obj.tutorial.slug)
            + f"#comment-{obj.pk}"
        )
