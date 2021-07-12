from django.test import TestCase
from model_bakery import baker
from learning.models import Category
from learning.querysets.category_queryset import CategoryQueryset


class CategoryQuerysetTest(TestCase):
    @classmethod
    def setUpClass(cls):
        active_categories: list[Category] = baker.make_recipe(
            "learning.active_category", _quantity=4
        )
        inactive_categories: list[Category] = baker.make_recipe(
            "learning.inactive_category", _quantity=6
        )
        cls.active_categories = active_categories
        cls.inactive_categories = inactive_categories

        super().setUpClass()

    def test_used_by_model(self):
        """Should be used as Category model's manager."""
        self.assertIsInstance(Category.objects.all(), CategoryQueryset)

    def test_active_categories(self):
        """active_categories should return queryset of active categories."""
        active_queryset = Category.objects.active_categories()
        self.assertEqual(list(active_queryset), self.active_categories)
