from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker
from authentication.email_confirmation import confirm_email_token

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
