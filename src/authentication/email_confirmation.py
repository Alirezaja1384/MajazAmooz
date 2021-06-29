import logging
from typing import Optional
from smtplib import SMTPException
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_text
from django.db import DatabaseError

from authentication.models import User


logger = logging.getLogger("emails")

UserModel = get_user_model()


class ConfirmEmailTokenGenerator(PasswordResetTokenGenerator):
    """Generates user email confirmation token"""

    def _make_hash_value(self, user: User, timestamp) -> str:
        return f"{user.id}{timestamp}{user.email_confirmed}"


confirm_email_token = ConfirmEmailTokenGenerator()


class EmailConfirmationManager:
    """This class manages user email confirmation
    includes generating uid and token,
    sending email, validating and confirming email
    """

    def __init__(self, user: User):
        self.user = user

    @staticmethod
    def validate(uid_base64: str, token: str) -> UserModel:
        """Validates token by base64 encoded user id

        Args:
            uid_base64 (str): Base64 encoded user id
            token (str): Email validation token

        Returns:
            bool: Returns user if token was valid
                  and None if it wasn't
        """
        try:
            # decode user id
            uid = force_text(urlsafe_base64_decode(uid_base64))
            # get user by decoded user id
            user = UserModel.objects.get(id=uid)

            # check token is valid or not
            if confirm_email_token.check_token(user, token):
                return user

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

    def get_uid_base64(self):
        return urlsafe_base64_encode(force_bytes(self.user.pk))

    def get_token(self):
        return confirm_email_token.make_token(self.user)

    def send_mail(
        self,
        template: str,
        confirm_url: str,
        from_email: str,
        subject: Optional[str] = "تایید ایمیل",
        plain_message: Optional[str] = None,
    ) -> bool:
        """Sends email confirmation mail to given user on initialization

        Args:
            template (str): Template path for html message
            confirm_url (str): Email confirmation url
            from_email (str): From email address
            subject (Optional[str], optional): Email subject.
                Defaults to 'تایید ایمیل'.
            plain_message (Optional[str], optional): Plain text message.
                Defaults to None.

        Returns:
            bool: returns True if sending email was successfull
                    and returns False if it wasn't.
        """

        if not plain_message:
            plain_message = (
                f"سلام {self.user.get_full_name()} عزیز، "
                + f"لینک تایید ایمیل شما {confirm_url}"
            )

        html_message = render_to_string(
            template,
            {"subject": subject, "user": self.user, "url": confirm_url},
        )

        email = EmailMultiAlternatives(
            subject, plain_message, from_email, to=[self.user.email]
        )
        email.attach_alternative(html_message, "text/html")

        try:
            email.send()
            return True
        except SMTPException as ex:
            logger.warning(ex)
            return False

    def confirm(self) -> bool:
        """Confirms user account
            * Sets user.email_confirmed = True
            * Gives email_confirmed permission

        Args:
            uid_base64 (str): Base64 encoded user id
            token (str): Email validation token

        Returns:
            bool: True if confirmation was successful
                  and False if it wasn't.
        """
        try:
            # Set email_confirmed to True
            self.user.email_confirmed = True
            self.user.save()

            # Give email_confirmed permission to user
            permission = Permission.objects.get(codename="email_confirmed")
            self.user.user_permissions.add(permission)

            return True
        except DatabaseError:
            return False
