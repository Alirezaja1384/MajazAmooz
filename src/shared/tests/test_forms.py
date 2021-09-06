from django import forms
from django.test import TestCase
from crispy_forms.layout import Submit
from shared.forms import CrispySubmitButtonMixin


class CrispySubmitButtonMixinTest(TestCase):
    class TestForm(CrispySubmitButtonMixin, forms.Form):
        name = forms.CharField(required=False)

        class Meta:
            submit_btn_text = "Test"
            submit_btn_class = "test-cls"

    def setUp(self):
        self.form_instance = self.TestForm()
        self.last_helper_input: Submit = self.form_instance.helper.inputs[-1]

    def test_form_has_helper(self):
        """Form should have helper."""
        self.assertTrue(hasattr(self.form_instance, "helper"))

    def test_form_helper_submit_button(self):
        """Form helper's last input should be a submit button."""
        self.assertIsInstance(self.last_helper_input, Submit)

    def test_submit_btn_text(self):
        """Meta class's submit_btn_text should be used as
        submit button's value (text).
        """
        self.assertEqual(
            self.form_instance.Meta.submit_btn_text,
            self.last_helper_input.value,
        )

    def test_submit_btn_class(self):
        """Meta class's submit_btn_class should be in submit
        button's class.
        """
        self.assertIn(
            self.form_instance.Meta.submit_btn_class,
            self.last_helper_input.field_classes,
        )
