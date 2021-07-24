from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory
from model_bakery import baker
from shared.models import ConfirmStatusChoices
from learning.models import Tutorial, TutorialComment
from learning.admin import actions


@patch.object(actions, "TutorialConfirmDisproveNotifier")
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
        self.assertTrue(mock.return_value.notify.called)

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


class TutorialCommentAdminActionsTest(TestCase):
    notifier_classes = [
        "TutorialCommentConfirmDisproveNotifier",
        "TutorialCommentReplyNotifier",
        "TutorialAuthorNewConfirmedCommentNotifier",
    ]

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        cls.modeladmin = MagicMock()

        super().setUpClass()

    def setUp(self):
        # Patchers
        self.notifier_patchers = {
            notifier: patch.object(actions, notifier)
            for notifier in self.notifier_classes
        }

        # Mocked classes' instances
        self.notifier_instances = {
            patcher[0]: patcher[1].start().return_value
            for patcher in self.notifier_patchers.items()
        }

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

    def test_confirm_action_confirm_tutorial_comments(self):
        """Confirm action should confirm given queryset objects."""
        self.confirm_queryset()

        # No non-confirmed object should exist
        self.assertFalse(
            self.queryset.exclude(
                confirm_status=ConfirmStatusChoices.CONFIRMED
            ).exists()
        )

    def test_confirm_action_call_notifiers(self):
        """Confirm action should call all mocked notifiers."""
        self.confirm_queryset()

        self.assertTrue(
            self.notifier_instances[
                "TutorialCommentConfirmDisproveNotifier"
            ].notify.called
        )
        self.assertTrue(
            self.notifier_instances[
                "TutorialCommentReplyNotifier"
            ].notify.called
        )
        self.assertTrue(
            self.notifier_instances[
                "TutorialAuthorNewConfirmedCommentNotifier"
            ].notify.called
        )

    def test_confirm_action_message_user(self):
        """Confirm action should call given modeladmin's message_user()."""
        self.confirm_queryset()
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_disprove_tutorial_comments(self):
        """Disprove action should disprove given queryset objects."""
        self.disprove_queryset()
        # No non-disproved object should exist
        self.assertFalse(
            self.queryset.exclude(
                confirm_status=ConfirmStatusChoices.DISPROVED
            ).exists()
        )

    def test_disprove_action_message_user(self):
        """Disprove action should call given modeladmin's message_user()."""
        self.disprove_queryset()
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_call_notifiers(self):
        """Disprove action should only call confirm_disprove notifier."""
        self.disprove_queryset()

        # Call confirm_disprove notifier
        self.assertTrue(
            self.notifier_instances[
                "TutorialCommentConfirmDisproveNotifier"
            ].notify.called
        )
        # Don't call others
        self.assertFalse(
            self.notifier_instances[
                "TutorialCommentReplyNotifier"
            ].notify.called
        )
        self.assertFalse(
            self.notifier_instances[
                "TutorialAuthorNewConfirmedCommentNotifier"
            ].notify.called
        )

    def tearDown(self):
        for patcher in self.notifier_patchers.values():
            patcher.stop()
