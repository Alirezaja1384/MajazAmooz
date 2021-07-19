import random
from smtplib import SMTPException
from unittest import mock
from django.test import TestCase
from model_bakery import baker
from learning import emails


class EmailsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        tutorials = baker.make_recipe("learning.tutorial", _quantity=5)
        baker.make_recipe(
            "learning.tutorial_comment",
            tutorial=random.choice(tutorials),
            _quantity=10,
        )

    def setUp(self):
        self.logger_pathcher = mock.patch.object(emails, "logger")
        self.email_cls_pathcher = mock.patch.object(
            emails, "EmailMultiAlternatives"
        )

        self.logger_mock = self.logger_pathcher.start()
        self.email_cls_mock = self.email_cls_pathcher.start()
        self.email_instance_mock = self.email_cls_mock.return_value

    def send_email(self, *args, **kwargs):
        if not args:
            args = (
                "subject",
                ["testmail@mail.com"],
            )

        return emails.send_mail(*args, **kwargs)

    def test_send_mail_call_send(self):
        """Should call EmailMultiAlternatives instance's send method."""
        self.send_email()
        self.assertTrue(self.email_instance_mock.send.called)

    def test_send_mail_smtp_exception_return_false(self):
        """Should return False if EmailMultiAlternatives instance's
        save method raise SMTPException.
        """
        # send() will raise SMTPException
        self.email_instance_mock.send.side_effect = SMTPException()
        self.assertFalse(self.send_email())

    def test_send_mail_smtp_exception_log_warning(self):
        """Should log exception as warning if EmailMultiAlternatives
        instance's save method raise SMTPException.
        """
        self.email_instance_mock.send.side_effect = SMTPException()
        self.send_email()

        self.logger_mock.warning.assert_called_with(
            self.email_instance_mock.send.side_effect
        )

    @mock.patch.object(emails, "render_to_string")
    def test_send_mail_render_template(
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

    def tearDown(self):
        self.logger_pathcher.stop()
        self.email_cls_pathcher.stop()
