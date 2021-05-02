from django import forms

from learning.models import TutorialComment


class TutorialCommentForm(forms.ModelForm):
    class Meta:
        model = TutorialComment
        fields = ('title', 'body', 'allow_reply', 'notify_replies',
                  'tutorial', 'user', 'parent_comment')
