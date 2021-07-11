from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory
from model_bakery import baker
from shared.models import ConfirmStatusChoices
from learning.models import Tutorial
from learning.admin import actions


@patch("learning.admin.actions.notify_tutorial_confirm_disprove")
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

    def test_confirm_action_confirm_tutorials(self, _: MagicMock):
        """confirm_tutorial_action should confirm given tutorial queryset.

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        actions.confirm_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/confirm_tutorial"),
            self.queryset,
        )

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
        actions.confirm_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/confirm_tutorial"),
            self.queryset,
        )
        self.assertTrue(mock.called)

    def test_confirm_action_message_user(self, _: MagicMock):
        """Confirm action should call given modeladmin's message_user().

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        actions.confirm_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/confirm_tutorial"),
            self.queryset,
        )
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_disprove_tutorials(self, _: MagicMock):
        """Disprove action should disprove given queryset objects.

        Args:
            _ (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        actions.disprove_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/disprove_tutorial"),
            self.queryset,
        )

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
        actions.disprove_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/confirm_tutorial"),
            self.queryset,
        )
        self.assertTrue(self.modeladmin.message_user.called)

    def test_disprove_action_call_notifiers(self, mock: MagicMock):
        """Disprove action should call notify_tutorial_confirm_disprove().

        Args:
            mock (MagicMock): Mocked notify_tutorial_confirm_disprove method.
        """
        actions.disprove_tutorial_action(
            self.modeladmin,
            self.factory.get("/admin/disprove_tutorial"),
            self.queryset,
        )
        self.assertTrue(mock.called)
