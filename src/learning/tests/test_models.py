from copy import deepcopy
from django.test import TestCase
from django.core.exceptions import ValidationError
from model_bakery import baker
from learning.models import Category, Tutorial, TutorialComment
from shared.models import ConfirmStatusChoices


class CategoryTest(TestCase):
    def setUp(self):
        self.category: Category = baker.make_recipe(
            "learning.active_category",
            name="a test category",
            slug="different-slug",
        )

    def test_auto_slug(self):
        """Model baker sets slug automatically but category should generate
        slug automatically even if it set on initialization.
        """
        self.assertEqual(self.category.slug, "a-test-category")

    def test_not_allow_self_parent(self):
        """Category's clean() method should raise validation error
        when category's parent is itself.
        """
        # set parent category to itself
        self.category.parent_category = self.category
        self.assertRaises(ValidationError, self.category.clean)


class TutorialTest(TestCase):
    def setUp(self):
        tutorial: Tutorial = baker.make_recipe("learning.tutorial")
        tutorial.body = "Changed body"
        # confirm_status should not effect because a
        # sensitive data (body) has been changed
        tutorial.confirm_status = ConfirmStatusChoices.CONFIRMED
        tutorial.save()

        self.changed_tutorial = tutorial

    def test_auto_slug(self):
        """Model baker sets slug automatically but category should generate
        slug automatically even if it set on initialization.
        """
        tutorial: Tutorial = baker.make_recipe(
            "learning.tutorial",
            title="A tutorial title",
            slug="different-slug",
        )
        self.assertEqual(tutorial.slug, "a-tutorial-title")

    def test_edit_is_edited(self):
        """Should set 'is_edited=True' if a sensitive data (like body)
        change.
        """
        self.assertTrue(self.changed_tutorial.is_edited)

    def test_edit_last_edit_date(self):
        """Should set 'last_edit_date' if a sensitive data (like body)
        change.
        """
        self.assertIsNotNone(self.changed_tutorial.last_edit_date)

    def test_edit_waiting_for_confirm(self):
        """Should set 'confirm_status' to waiting for confirm
        if a sensitive data (like body) change.
        """
        self.assertEqual(
            self.changed_tutorial.confirm_status,
            ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        )


class TutorialCommentTest(TestCase):
    def setUp(self):
        tutorial: Tutorial = baker.make_recipe("learning.tutorial")

        comment: TutorialComment = baker.make_recipe(
            "learning.tutorial_comment", tutorial=tutorial
        )
        replied_comment: TutorialComment = baker.make_recipe(
            "learning.tutorial_comment", parent_comment=comment
        )

        self.tutorial = tutorial
        self.comment = comment
        self.replied_comment = replied_comment

    def test_not_allow_self_parent(self):
        """Should not allow comment to be parent of itself."""
        self.comment.parent_comment = self.comment
        self.assertRaises(ValidationError, self.comment.clean)

    def test_automatically_set_tutorial_on_replay(self):
        """Should automatically set replied comment's tutorial to
        its parents's tutorial.
        """
        self.assertEqual(self.replied_comment.tutorial, self.comment.tutorial)

    def test_on_edit(self):
        """Should set 'is_edited=True', 'last_edit_date', and
        set 'confirm_status' to 'WAITING_FOR_CONFIRM'.
        """
        edited_comment = deepcopy(self.comment)
        edited_comment.body = "Changed body"
        edited_comment.confirm_status = ConfirmStatusChoices.CONFIRMED
        edited_comment.save()

        self.assertTrue(edited_comment.is_edited)
        self.assertIsNotNone(edited_comment.last_edit_date)
        self.assertEqual(
            edited_comment.confirm_status,
            ConfirmStatusChoices.WAITING_FOR_CONFIRM,
        )
