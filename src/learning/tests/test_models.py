from django.test import TestCase
from django.core.exceptions import ValidationError
from model_bakery import baker
from learning.models import Category, Tutorial
from shared.models import ConfirmStatusChoices


class TestCategory(TestCase):
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

    def test_not_accept_self_parent(self):
        """Category's clean() method should raise validation error
        when category's parent is itself.
        """
        # set parent category to itself
        self.category.parent_category = self.category
        self.assertRaises(ValidationError, self.category.clean)


class TestTutorial(TestCase):
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
