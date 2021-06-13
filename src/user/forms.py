from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from learning.models import (Tutorial, TutorialComment)


UserModel = get_user_model()


class TutorialForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add submit button
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'انجام', css_class='btn-success'))

    class Meta:
        model = Tutorial
        fields = ('title', 'short_description', 'body',
                  'image', 'categories', 'is_active',)


class TutorialCommentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add submit button
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'انجام', css_class='btn-success'))

    class Meta:
        model = TutorialComment
        fields = ('title', 'body', 'allow_reply',
                  'notify_replies', 'is_active',)


class UserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add submit button
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('create_update', 'انجام', css_class='btn-success'))

        # Make extra_required_fields required in form
        for field in self.Meta.extra_required_fields:
            self.fields[field].required = True

    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'avatar', 'tutorials_count_goal',
                  'comments_count_goal', 'likes_count_goal', 'views_count_goal',)

        extra_required_fields = (
            'first_name',
            'last_name',
        )
