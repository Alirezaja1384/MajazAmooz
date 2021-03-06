from typing import Optional
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError
from learning.models import Tutorial, TutorialComment, TutorialTag
from shared.forms import CrispySubmitButtonMixin, ExtraRequiredFieldsMixin


UserModel = auth.get_user_model()


class TutorialTagForm(forms.ModelForm):
    class Meta:
        model = TutorialTag
        fields = ("title",)


class TutorialForm(forms.ModelForm, CrispySubmitButtonMixin):

    tags = forms.CharField(required=False, label="کلمات کلیدی")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Define save_tags that returns None
        # it will be a reference to _save_tags
        # if form save(commit=False) be called
        self.save_tags = lambda self: None

        # If editing model, fill tags input with current tags
        instance: Optional[Tutorial] = kwargs.get("instance")
        if instance:
            # Join tag titles with ','
            self.fields["tags"].initial = ",".join(
                [tag.title for tag in instance.tags.all()]
            )

    def clean_tags(self) -> list[TutorialTag]:
        """Convert tags from string to list of TutorialTag objects
            and validate them.

        Raises:
            ValidationError: If any tag doesn't validate it raises
                             ValidationError and describes the error.

        Returns:
            list[TutorialTag]: TutorialTag instances if all of them were valid.
        """
        tag_instances: list[TutorialTag] = []

        # Split non-blank tags by ',' and assign tag name's to tag_titles list
        tag_titles: list[str] = [
            tag
            for tag in self.cleaned_data.get("tags", "").split(",")
            if tag != ""
        ]

        for tag_title in tag_titles:
            # create form to validate tutorial tag
            tag_form = TutorialTagForm({"title": tag_title})

            # Validate form
            if not tag_form.is_valid():
                # Just raise errors (without its field name)
                raise ValidationError(
                    [
                        f"{err[0]}: {err[1][0]}"
                        for err in tag_form.errors.items()
                    ]
                )

            # Set tag's tutorial
            tag_form.instance.tutorial = self.instance
            # Add to tags list
            tag_instances.append(tag_form.instance)

        # return list of tag objects
        return tag_instances

    def _save_tags(self):
        """Saves tutorial tags if tags changed and sets
        tutorial's confirm_status to wating for confirm
        if tags changed and tutorial was confirmed before.
        """
        # If tag has been changed
        if "tags" in self.changed_data:
            tutorial: Tutorial = self.instance

            # Delete old tags
            tutorial.tags.all().delete()
            # Create new tags
            TutorialTag.objects.bulk_create(self.cleaned_data["tags"])

            # Do BEFORE_UPDATE actions for tutorial and save them
            # when tags edited
            tutorial.on_edit()
            tutorial.save()

    def save(self, commit=True) -> Tutorial:
        """Saves tutorial and tags(if commit=True)

        Notes:
            - If you set commit=False you should call save_tags manually
              to save tags.

        Args:
            commit (bool, optional): Saves tutorial object if True,
                otherwise doesn't. Defaults to True.

        Returns:
            Tutorial: Tutorial instance created by form.
        """
        # Call main save method
        tutorial = super().save(commit=commit)

        if commit:
            # If commit=True save tag automatically
            self._save_tags()
        else:
            # Otherwise add save_tags function to object that
            # references to self._save_tags
            self.save_tags = self._save_tags

        # return tutorial instance
        return tutorial

    class Meta:
        model = Tutorial
        fields = (
            "title",
            "short_description",
            "body",
            "image",
            "categories",
            "tags",
            "is_active",
        )


class TutorialCommentForm(forms.ModelForm, CrispySubmitButtonMixin):
    class Meta:
        model = TutorialComment
        fields = (
            "title",
            "body",
            "allow_reply",
            "notify_replies",
            "is_active",
        )

        help_texts = {
            "tags": "برای جداسازی از 'Enter' یا ',' استفاده کنید",
        }


class UserProfileForm(
    forms.ModelForm, CrispySubmitButtonMixin, ExtraRequiredFieldsMixin
):
    class Meta:
        model = UserModel
        fields = (
            "first_name",
            "last_name",
            "avatar",
            "tutorials_count_goal",
            "comments_count_goal",
            "likes_count_goal",
            "views_count_goal",
        )

        extra_required_fields = (
            "first_name",
            "last_name",
        )


class PasswordChangeForm(
    auth.forms.PasswordChangeForm, CrispySubmitButtonMixin
):
    class Meta:
        submit_btn_text = "تغییر گذرواژه"
