import abc
import random
from typing import Type
from unittest import mock
from smtplib import SMTPException
from django.test import TestCase, RequestFactory
from django.db.models import Model, QuerySet
from django.core.exceptions import ImproperlyConfigured
from model_bakery import baker
from learning import notifications
from learning.models import Tutorial, TutorialComment


class AbstractQuerysetNotifierTest(TestCase):
    class TestQuerysetNotifier(notifications.AbstractQuerysetNotifier):
        pass

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        # Make tutorials
        baker.make_recipe("learning.tutorial", _quantity=2)

    def setUp(self):
        self.logger_pathcher = mock.patch.object(notifications, "logger")
        self.email_cls_pathcher = mock.patch.object(
            notifications, "EmailMultiAlternatives"
        )

        self.logger_mock = self.logger_pathcher.start()
        self.email_instance_mock = self.email_cls_pathcher.start().return_value

    def send_email(self, *args, **kwargs) -> bool:
        """Sends email using AbstractQuerysetNotifier.send_email

        Returns:
            bool: Result of send_email() method.
        """
        if not args:
            args = (
                "subject",
                ["testmail@mail.com"],
            )

        return notifications.AbstractQuerysetNotifier.send_email(
            *args, **kwargs
        )

    def test_send_email_call_send(self):
        """Should call EmailMultiAlternatives instance's send method."""
        self.send_email()
        self.assertTrue(self.email_instance_mock.send.called)

    def test_send_email_smtp_exception_return_false(self):
        """Should return False if EmailMultiAlternatives instance's
        save method raise SMTPException.
        """
        # send() will raise SMTPException
        self.email_instance_mock.send.side_effect = SMTPException()
        self.assertFalse(self.send_email())

    def test_send_email_smtp_exception_log_warning(self):
        """Should log exception as warning if EmailMultiAlternatives
        instance's save method raise SMTPException.
        """
        self.email_instance_mock.send.side_effect = SMTPException()
        self.send_email()

        self.logger_mock.warning.assert_called_with(
            self.email_instance_mock.send.side_effect
        )

    @mock.patch.object(notifications, "render_to_string")
    def test_send_email_render_template(
        self, render_to_string_mock: mock.MagicMock
    ):
        """Should call render_to_string with given template and context
        when template is not None.
        """
        template = "test_template.txt"
        context = {"key": "value"}
        self.send_email(
            "subject",
            ["testmail@mail.com"],
            template=template,
            context=context,
        )

        render_to_string_mock.assert_called_with(template, context)

    def test_notify_call_notify_by_email(self):
        """notify() should call notify_by_email() for each model object
        in the queryset.
        """
        notifier_instance = self.TestQuerysetNotifier(
            self.factory.get("/"), Tutorial.objects.all()
        )

        with mock.patch.object(
            notifier_instance, "notify_by_email"
        ) as notify_by_email_mock:
            notifier_instance.notify()
            self.assertEqual(
                notify_by_email_mock.call_count,
                notifier_instance.get_queryset().count(),
            )

    def test_notify_result_success_count(self):
        """Should correctly calculate count of successful notifications."""
        notifier_instance = self.TestQuerysetNotifier(
            self.factory.get("/"), Tutorial.objects.all()
        )

        with mock.patch.object(
            notifier_instance, "notify_by_email", return_value=True
        ):
            result = notifier_instance.notify()
            self.assertEqual(
                result.success, notifier_instance.get_queryset().count()
            )

    def test_notify_result_failed_count(self):
        """Should correctly calculate count of failed notifications."""
        notifier_instance = self.TestQuerysetNotifier(
            self.factory.get("/"), Tutorial.objects.all()
        )

        with mock.patch.object(
            notifier_instance, "notify_by_email", return_value=False
        ):
            result = notifier_instance.notify()
            self.assertEqual(
                result.failed, notifier_instance.get_queryset().count()
            )

    def tearDown(self):
        self.logger_pathcher.stop()
        self.email_cls_pathcher.stop()


class _QuerysetNotifierBaseTest(TestCase, metaclass=abc.ABCMeta):
    notifier_cls: notifications.AbstractQuerysetNotifier
    notifier_object_type: Type[Model]

    @classmethod
    def setUpClass(cls):

        if not hasattr(cls, "notifier_cls") or not hasattr(
            cls, "notifier_object_type"
        ):
            raise ImproperlyConfigured(
                "notifier_cls and notifier_object_type should be configured."
            )

        cls.queryset = cls.notifier_object_type.objects.all()
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        tutorials = baker.make_recipe("learning.tutorial", _quantity=4)
        baker.make_recipe(
            "learning.tutorial_comment", tutorial=None, _quantity=4
        )
        baker.make_recipe(
            "learning.tutorial_comment",
            tutorial=random.choice(tutorials),
            _quantity=4,
        )

    def setUp(self):
        self.logger_pathcher = mock.patch.object(notifications, "logger")
        self.email_cls_pathcher = mock.patch.object(
            notifications, "EmailMultiAlternatives"
        )

        self.logger_mock = self.logger_pathcher.start()
        self.email_instance_mock = self.email_cls_pathcher.start().return_value

    def get_notifier_queryset(self) -> QuerySet:
        notifier = self.notifier_cls(self.factory.get("/"), self.queryset)
        return notifier.get_queryset().order_by()

    def test_notify_by_email_call_send_email(self):
        """notify_by_email() should call send_email() once."""
        notifier = self.notifier_cls(self.factory.get("/"), mock.MagicMock())

        with mock.patch.object(notifier, "send_email") as send_email_mock:
            notifier.notify_by_email(mock.MagicMock())
            send_email_mock.assert_called_once()

    def test_build_url(self):
        """build_url() should not return None."""
        notifier = self.notifier_cls(
            self.factory.get("/"), self.notifier_object_type.objects.all()
        )
        self.assertIsNotNone(notifier.build_url(notifier.queryset.first()))

    def tearDown(self):
        self.logger_pathcher.stop()
        self.email_cls_pathcher.stop()


class TutorialConfirmDisproveNotifierTest(_QuerysetNotifierBaseTest):
    notifier_object_type = Tutorial
    notifier_cls = notifications.TutorialConfirmDisproveNotifier

    def test_not_include_waiting_for_confirm(self):
        """queryset should not include waiting for confirm tutorials."""
        waiting_for_confirm = baker.make_recipe(
            "learning.waiting_for_confirm_tutorial"
        )
        qs = self.get_notifier_queryset()

        self.assertNotIn(waiting_for_confirm, qs)


class TutorialCommentConfirmDisproveNotifierTest(_QuerysetNotifierBaseTest):
    notifier_object_type = TutorialComment
    notifier_cls = notifications.TutorialCommentConfirmDisproveNotifier

    def test_not_include_waiting_for_confirm(self):
        """queryset should not include waiting for confirm objects."""
        waiting_for_confirm = baker.make_recipe(
            "learning.waiting_for_confirm_tutorial_comment"
        )
        qs = self.get_notifier_queryset()

        self.assertNotIn(waiting_for_confirm, qs)

    def test_not_include_without_user(self):
        """queryset should not include objects without user."""
        # Make a tutorial comment without user
        without_user = baker.make_recipe(
            "learning.confirmed_tutorial_comment", user=None
        )
        qs = self.get_notifier_queryset()

        # Should not include this one
        self.assertNotIn(without_user, qs)

    def test_not_include_without_tutorial(self):
        """queryset should not include objects without tutorial."""
        # Make a tutorial comment without tutorial
        without_tutorial = baker.make_recipe(
            "learning.confirmed_tutorial_comment", tutorial=None
        )
        qs = self.get_notifier_queryset()

        # Should not include this one
        self.assertNotIn(without_tutorial, qs)


class TutorialAuthorNewConfirmedCommentNotifierTest(_QuerysetNotifierBaseTest):
    notifier_object_type = TutorialComment
    notifier_cls = notifications.TutorialAuthorNewConfirmedCommentNotifier

    def test_not_include_waiting_for_confirm(self):
        """queryset should not include waiting for confirm objects."""
        waiting_for_confirm_tutorial = baker.make_recipe(
            "learning.waiting_for_confirm_tutorial_comment"
        )
        qs = self.get_notifier_queryset()

        self.assertNotIn(waiting_for_confirm_tutorial, qs)

    def test_not_include_without_tutorial(self):
        """queryset should not include objects without tutorial."""
        # Make a tutorial comment without tutorial
        without_tutorial = baker.make_recipe(
            "learning.confirmed_tutorial_comment", tutorial=None
        )
        qs = self.get_notifier_queryset()

        # Should not include this one
        self.assertNotIn(without_tutorial, qs)

    def test_not_include_without_tutorial_author(self):
        """queryset should not include objects without tutorial author."""
        # Make a tutorial comment that its tutorial doesn't have author
        without_tutorial_author = baker.make_recipe(
            "learning.confirmed_tutorial_comment",
            is_active=True,
            tutorial=baker.make_recipe(
                "learning.confirmed_tutorial", author=None
            ),
        )
        qs = self.get_notifier_queryset()

        # Should not include this one
        self.assertNotIn(without_tutorial_author, qs)


# Delete it to prevent testing itself!
del _QuerysetNotifierBaseTest
