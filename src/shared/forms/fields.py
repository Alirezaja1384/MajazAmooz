from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class CrispySubmitButtonMixin(forms.Form):
    """Adds submit button to crispy forms.

    Meta class options:
        submit_btn_text : Submit button's text.
        submit_btn_class : Submit button's css class.
    """

    class Meta:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add submit button
        self.helper = FormHelper()
        self.helper.add_input(
            Submit(
                "create_update",
                getattr(self.Meta, "submit_btn_text", "انجام"),
                css_class=getattr(
                    self.Meta, "submit_btn_class", "btn-success"
                ),
            )
        )


class ExtraRequiredFieldsMixin(forms.Form):
    """Makes Meta class's extra_required_fields required.

    Meta class options:
        extra_required_fields : Iterable of field names
            to make them required.
    """

    class Meta:
        extra_required_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make extra_required_fields required in form
        for field in getattr(self.Meta, "extra_required_fields", []):
            self.fields[field].required = True
