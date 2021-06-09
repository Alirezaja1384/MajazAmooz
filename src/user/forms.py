from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from tinymce.widgets import TinyMCE

from learning.models import (Tutorial, TutorialComment)


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


class TutorialCommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'انجام', css_class='btn-success'))

    class Meta:
        model = TutorialComment
        fields = ('title', 'body', 'allow_reply',
                  'notify_replies', 'is_active',)

        widgets = {
            'body': TinyMCE(),
        }
