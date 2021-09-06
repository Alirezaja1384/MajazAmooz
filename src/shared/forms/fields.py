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
