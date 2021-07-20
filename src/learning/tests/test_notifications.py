import random
from smtplib import SMTPException
from unittest import mock
from django.test import TestCase, RequestFactory
from model_bakery import baker
from shared.models import ConfirmStatusChoices
from learning import notifications
from learning.models import Tutorial


class NotificationsTest(TestCase):
    class TestQuerysetNotifier(notifications.AbstractQuerysetNotifier):
        pass

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        confirmed_tutorials = baker.make_recipe(
            "learning.confirmed_tutorial", _quantity=2
        )
        disproved_tutorials = baker.make_recipe(
            "learning.disproved_tutorial", _quantity=2
        )
        baker.make_recipe(
            "learning.tutorial_comment",
            tutorial=random.choice(confirmed_tutorials + disproved_tutorials),
            _quantity=10,
        )

        cls.confirmed_disproved_tutorials = Tutorial.objects.exclude(
            confirm_status=ConfirmStatusChoices.WAITING_FOR_CONFIRM
        )

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

    def test_notifier_send_email_call_send(self):
        """Should call EmailMultiAlternatives instance's send method."""
        self.send_email()
        self.assertTrue(self.email_instance_mock.send.called)

    def test_notifier_send_email_smtp_exception_return_false(self):
        """Should return False if EmailMultiAlternatives instance's
        save method raise SMTPException.
        """
        # send() will raise SMTPException
        self.email_instance_mock.send.side_effect = SMTPException()
        self.assertFalse(self.send_email())

    def test_notifier_send_email_smtp_exception_log_warning(self):
        """Should log exception as warning if EmailMultiAlternatives
        instance's save method raise SMTPException.
        """
        self.email_instance_mock.send.side_effect = SMTPException()
        self.send_email()

        self.logger_mock.warning.assert_called_with(
            self.email_instance_mock.send.side_effect
        )

    @mock.patch.object(notifications, "render_to_string")
    def test_notifier_send_email_render_template(
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

    def test_notifier_notify_call_notify_by_email(self):
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

    def test_notifier_notify_result_success_count(self):
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

    def test_notifier_notify_result_failed_count(self):
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
