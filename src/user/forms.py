from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from tinymce.widgets import TinyMCE

from learning.models import Tutorial


class TutorialForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'انجام', css_class='btn-success'))

    class Meta:
        model = Tutorial
        fields = ('title', 'short_description', 'body',
                  'image', 'categories', 'is_active',)

        widgets = {
            'body': TinyMCE(),
        }


class DeleteForm(forms.Form):

    CHOICES = [
        ('deactivate', 'غیر فعالسازی'),
        ('delete', 'حذف'),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'حذف', css_class='btn-danger'))

    action = forms.ChoiceField(choices=CHOICES, required=True,
                               initial='deactivate', label='عملیات مورد نظر',
                               widget=forms.RadioSelect)

    @property
    def get_action_display(self):
        return dict(self.fields['action'].choices)[self.cleaned_data['action']]
