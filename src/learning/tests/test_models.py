from django.test import TestCase
from django.core.exceptions import ValidationError
from model_bakery import baker
from learning.models import Category


class TestCategory(TestCase):
    def setUp(self):
        self.category: Category = baker.make_recipe(
            "learning.active_category", name="a test category"
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
