import base64
from django.core import mail
from django.test import TestCase
from django.shortcuts import resolve_url
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from model_bakery import baker
from authentication.email_confirmation import (
    EmailConfirmationManager,
    confirm_email_token,
)

User = get_user_model()


class ConfirmEmailTokenGeneratorTest(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.token_generator = confirm_email_token
        self.token = self.token_generator.make_token(self.user)

    def test_generate_token(self):
        """Generated token should not be None."""
        self.assertIsNotNone(self.token)

    def test_token_validation(self):
        """Generated token should be valid."""
        self.assertTrue(
            self.token_generator.check_token(self.user, self.token)
        )

    def tests_depend_on_email_confirmed(self):
        """Generated token should depend on user's email_confirmed."""
        # Change user's email confirmation status
        self.user.email_confirmed = True
        self.user.save()

        self.assertFalse(
            self.token_generator.check_token(self.user, self.token)
        )

    def tests_not_depend_on_other_fields(self):
        """Generated token should not depend on any other
        field of user (just email_confirmed and id).
        """
        # Change user's username
        self.user.username = "new_username"
        self.user.save()

        self.assertTrue(
            self.token_generator.check_token(self.user, self.token)
        )


class EmailConfirmationManagerTest(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.confirmation_manager = EmailConfirmationManager(self.user)

    def test_base64uid_base64_encoded(self):
        """Encoded user id should be correct."""
        uid_base64 = self.confirmation_manager.get_uid_base64()
        uid = force_str(
            # b"==" is padding to prevent invalid padding error
            base64.b64decode(force_bytes(uid_base64, "ascii") + b"==")
        )
        self.assertEqual(uid, force_str(self.user.pk))

    def test_get_token(self):
        """Generated token by get_token() should be valid."""
        token = self.confirmation_manager.get_token()
        self.assertTrue(confirm_email_token.check_token(self.user, token))

    def test_send_mail(self):
        uid_base64 = self.confirmation_manager.get_uid_base64()
        token = self.confirmation_manager.get_token()
        confirm_url = resolve_url(
            "authentication:confirm_email", uid_base64=uid_base64, token=token
        )

        email_result = self.confirmation_manager.send_mail(
            "mails/email_confirmation.html", confirm_url
        )

        self.assertTrue(email_result)
        self.assertTrue(len(mail.outbox) > 0)

    def test_validate_invalid_data(self):
        validated_user = self.confirmation_manager.validate(
            "invalid_uid_base64", "invalid_token"
        )

        self.assertIsNone(validated_user)

    def test_validate_valid_data(self):
        validated_user = self.confirmation_manager.validate(
            self.confirmation_manager.get_uid_base64(),
            self.confirmation_manager.get_token(),
        )

        self.assertEqual(validated_user, self.user)

    def test_confirm(self):
        self.confirmation_manager.confirm()

        # Should set user.email_confirmed = True
        self.assertTrue(self.user.email_confirmed)

        # Should add email_confirmed to user permissions
        permission = Permission.objects.get(codename="email_confirmed")
        self.assertIn(permission, self.user.user_permissions.all())
