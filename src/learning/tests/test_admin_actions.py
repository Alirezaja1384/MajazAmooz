from unittest.mock import MagicMock, DEFAULT, patch
from django.test import TestCase, RequestFactory
from model_bakery import baker
from shared.models import ConfirmStatusChoices
from learning.models import Tutorial, TutorialComment
from learning.admin import actions


@patch.object(actions, "notify_tutorial_confirm_disprove")
class TutorialAdminActionsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        cls.modeladmin = MagicMock()

        super().setUpClass()

    def setUp(self):
        # Create 12 tutorials (7 confirmed and 5 disproved)
        baker.make_recipe("learning.confirmed_tutorial", _quantity=7)
        baker.make_recipe("learning.disproved_tutorial", _quantity=5)

        self.queryset = Tutorial.objects.all()

    def confirm_queryset(self):
        """Confirms queryset by calling confirm_tutorial_action"""
        actions.confirm_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/confirm_comments"),
            self.queryset,
        )

    def disprove_queryset(self):
        """Disproves queryset by calling disprove_tutorial_action"""
        actions.disprove_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/disprove_comments"),
            self.queryset,
        )

    def test_confirm_action_confirm_tutorials(self, _: MagicMock):
        """Confirm action should confirm given queryset objects.

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        self.confirm_queryset()

        # No non-confirmed object should exist
        self.assertFalse(
            self.queryset.exclude(
                confirm_status=ConfirmStatusChoices.CONFIRMED
            ).exists()
        )

    def test_confirm_action_call_notifiers(self, mock: MagicMock):
        """Confirm action should call notify_tutorial_confirm_disprove().

        Args:
            mock (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        self.confirm_queryset()
        self.assertTrue(mock.called)

    def test_confirm_action_message_user(self, _: MagicMock):
        """Confirm action should call given modeladmin's message_user().

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        self.confirm_queryset()
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_disprove_tutorials(self, _: MagicMock):
        """Disprove action should disprove given queryset objects.

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        self.disprove_queryset()

        # No non-disproved object should exist
        self.assertFalse(
            self.queryset.exclude(
                confirm_status=ConfirmStatusChoices.DISPROVED
            ).exists()
        )

    def test_disprove_action_message_user(self, _: MagicMock):
        """Disprove action should call given modeladmin's message_user().

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        self.disprove_queryset()
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_call_notifiers(self, mock: MagicMock):
        """Disprove action should call notify_tutorial_confirm_disprove().

        Args:
            mock (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        self.disprove_queryset()
        self.assertTrue(mock.called)


@patch.multiple(
    actions,
    notify_tutorial_comments_reply=DEFAULT,
    notify_tutorial_new_confirmed_comment=DEFAULT,
    notify_tutorial_comment_confirm_disprove=DEFAULT,
)
class TutorialCommentAdminActionsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        cls.modeladmin = MagicMock()

        super().setUpClass()

    def setUp(self):
        # Create 12 tutorial comments (7 confirmed and 5 disproved)
        baker.make_recipe("learning.confirmed_tutorial_comment", _quantity=7)
        baker.make_recipe("learning.disproved_tutorial_comment", _quantity=5)

        self.queryset = TutorialComment.objects.all()

    def confirm_queryset(self):
        """Confirms queryset by calling confirm_tutorial_comment_action"""
        actions.confirm_tutorial_comment_action(
            self.modeladmin,
            self.factory.get("/admin/confirm_tutorial_comments"),
            self.queryset,
        )

    def disprove_queryset(self):
        """Disproves queryset by calling disprove_tutorial_comment_action"""
        actions.disprove_tutorial_comment_action(
            self.modeladmin,
            self.factory.get("/admin/disprove_tutorial_comments"),
            self.queryset,
        )

    def test_confirm_action_confirm_tutorial_comments(self, **_):
        """Confirm action should confirm given queryset objects."""
        self.confirm_queryset()
        # No non-confirmed object should exist
        self.assertFalse(
            self.queryset.exclude(
                confirm_status=ConfirmStatusChoices.CONFIRMED
            ).exists()
        )

    def test_confirm_action_call_notifiers(
        self,
        notify_tutorial_comments_reply: MagicMock,
        notify_tutorial_new_confirmed_comment: MagicMock,
        notify_tutorial_comment_confirm_disprove: MagicMock,
    ):
        """Confirm action should call all mocked notifiers.

        Args:
            notify_tutorial_comments_reply (MagicMock): mocked
                notify_tutorial_comments_reply.

            notify_tutorial_new_confirmed_comment (MagicMock): Mocked
                notify_tutorial_new_confirmed_comment.

            notify_tutorial_comment_confirm_disprove (MagicMock): Mocked
                notify_tutorial_comment_confirm_disprove.
        """
        self.confirm_queryset()

        self.assertTrue(notify_tutorial_comments_reply.called)
        self.assertTrue(notify_tutorial_new_confirmed_comment.called)
        self.assertTrue(notify_tutorial_comment_confirm_disprove.called)

    def test_confirm_action_message_user(self, **_):
        """Confirm action should call given modeladmin's message_user()."""
        self.confirm_queryset()
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_disprove_tutorial_comments(self, **_):
        """Disprove action should disprove given queryset objects."""
        self.disprove_queryset()
        # No non-disproved object should exist
        self.assertFalse(
            self.queryset.exclude(
                confirm_status=ConfirmStatusChoices.DISPROVED
            ).exists()
        )

    def test_disprove_action_message_user(self, **_):
        """Disprove action should call given modeladmin's message_user()."""
        self.disprove_queryset()
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_call_notifiers(
        self,
        notify_tutorial_comments_reply: MagicMock,
        notify_tutorial_new_confirmed_comment: MagicMock,
        notify_tutorial_comment_confirm_disprove: MagicMock,
    ):
        """Disprove action should only call confirm_disprove notifier.

        Args:
            notify_tutorial_comments_reply (MagicMock): mocked
                notify_tutorial_comments_reply.

            notify_tutorial_new_confirmed_comment (MagicMock): Mocked
                notify_tutorial_new_confirmed_comment.

            notify_tutorial_comment_confirm_disprove (MagicMock): Mocked
                notify_tutorial_comment_confirm_disprove.
        """
        self.disprove_queryset()
        # Call confirm_disprove notifier
        self.assertTrue(notify_tutorial_comment_confirm_disprove.called)
        # Don't call others
        self.assertFalse(notify_tutorial_comments_reply.called)
        self.assertFalse(notify_tutorial_new_confirmed_comment.called)
