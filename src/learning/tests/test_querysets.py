import random
from django.test import TestCase
from model_bakery import baker
from authentication.models import User
from learning.models import (
    Category,
    Tutorial,
    TutorialComment,
    TutorialLike,
    TutorialView,
)
from learning.querysets.category_queryset import CategoryQueryset
from learning.querysets.tutorial_queryset import TutorialQueryset
from learning.querysets.tutorial_comment_queryset import (
    TutorialCommentQueryset,
)


class CategoryQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        active_categories: list[Category] = baker.make_recipe(
            "learning.active_category", _quantity=4
        )
        inactive_categories: list[Category] = baker.make_recipe(
            "learning.inactive_category", _quantity=6
        )
        cls.active_categories = active_categories
        cls.inactive_categories = inactive_categories

    def test_used_by_model(self):
        """Should be used as Category model's manager."""
        self.assertIsInstance(Category.objects.all(), CategoryQueryset)

    def test_active_categories(self):
        """active_categories should return queryset of active categories."""
        active_queryset = Category.objects.active_categories()
        self.assertEqual(list(active_queryset), self.active_categories)


class TutorialQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author: User = baker.make(User)
        baker.make_recipe(
            "learning.tutorial",
            is_active=True,
            author=author,
            _quantity=5,
        )
        active_confirmed: list[Tutorial] = baker.make_recipe(
            "learning.confirmed_tutorial",
            is_active=True,
            author=author,
            _quantity=3,
        )

        cls.tutorials_qs = Tutorial.objects.all()
        cls.active_confirmed_tutorials = active_confirmed

    def test_used_by_model(self):
        """Should be used as Tutorial model's manager."""
        self.assertIsInstance(self.tutorials_qs, TutorialQueryset)

    def test_active_and_confirmed_tutorials(self):
        """active_and_confirmed_tutorials should return queryset of
        active and confirmed tutorials.
        """
        active_confirmed_qs = (
            # Note: Call order_by() to reset default ordering
            self.tutorials_qs.active_and_confirmed_tutorials().order_by()
        )
        self.assertEqual(
            list(active_confirmed_qs), list(self.active_confirmed_tutorials)
        )

    def test_annonate_comments_count(self):
        """annonate_comments_count should annonate active and confirmed
        comments count.
        """
        random_tutorial = random.choice(self.tutorials_qs)

        confirmed_comments = baker.make_recipe(
            "learning.confirmed_tutorial_comment",
            is_active=True,
            tutorial=random_tutorial,
            _quantity=2,
        )
        baker.make_recipe(
            "learning.disproved_tutorial_comment",
            tutorial=random_tutorial,
            _quantity=3,
        )

        tutorials_with_annonation = Tutorial.objects.annonate_comments_count()
        self.assertEqual(
            tutorials_with_annonation.get(
                pk=random_tutorial.pk
            ).comments_count,
            len(confirmed_comments),
        )

    def test_only_main_fields(self):
        """only_main_fields should load all expected fields
        data (In fact they shouldn't be differed).
        """
        tutorial = self.tutorials_qs.only_main_fields().first()
        expected_fields = [
            "title",
            "slug",
            "short_description",
            "likes_count",
            "image",
        ]
        deferred_fields = tutorial.get_deferred_fields()

        # Non of these field should be defferred
        for field in expected_fields:
            self.assertNotIn(field, deferred_fields)

    def test_prefetch_active_categories(self):
        """prefetch_active_categories should prefetch active categories."""
        tutorial = Tutorial.objects.prefetch_active_categories().first()
        self.assertIn(
            "categories",
            tutorial._prefetched_objects_cache,
        )

    def test_prefetch_active_confirmed_comments(self):
        """prefetch_active_confirmed_comments should prefetch
        active and confirmed comments."""
        tutorial = (
            Tutorial.objects.prefetch_active_confirmed_comments().first()
        )
        self.assertIn("comments", tutorial._prefetched_objects_cache)

    def test_aggregate_statistics(self):
        """aggregate_statistics should aggregate tutorials_count,
        likes_count, views_count and comments_count.
        """
        total_tutorials_count = self.tutorials_qs.count()

        like_per_tutorial = 2
        view_per_tutorial = 3
        comment_per_tutorial = 1

        for tutorial in self.tutorials_qs:
            # Make comments
            # Note: use activa and confirmed tutorials because
            # aggregate_statistics just counts active and confitmed ones
            baker.make_recipe(
                "learning.confirmed_tutorial_comment",
                is_active=True,
                tutorial=tutorial,
                _quantity=comment_per_tutorial,
            )
            # Make views
            baker.make(
                TutorialView,
                tutorial=tutorial,
                _quantity=view_per_tutorial,
            )
            # Make likes
            baker.make(
                TutorialLike,
                tutorial=tutorial,
                _quantity=like_per_tutorial,
            )

        statistics = self.tutorials_qs.aggregate_statistics()

        self.assertEqual(statistics["tutorials_count"], total_tutorials_count)
        self.assertEqual(
            statistics["likes_count"],
            like_per_tutorial * total_tutorials_count,
        )
        self.assertEqual(
            statistics["views_count"],
            view_per_tutorial * total_tutorials_count,
        )
        self.assertEqual(
            statistics["comments_count"],
            comment_per_tutorial * total_tutorials_count,
        )

    def test_get_related_tutorials(self):
        """get_related_tutorials should return tutorials that have
        joint category with given tutorial
        """
        categories = baker.make_recipe("learning.category", _quantity=4)

        tutorial = random.choice(self.active_confirmed_tutorials)
        tutorial.categories.set(categories)

        joint_category_tutorials = baker.make_recipe(
            "learning.tutorial",
            # Choose 2 categories randomly
            categories=random.choices(categories, k=2),
            _quantity=5,
        )

        # Note: Call order_by() to reset default ordering
        related_tutorials = self.tutorials_qs.order_by().get_related_tutorials(
            tutorial,
            # Get n related tutorials which n is count of
            # tutorials with joint category
            len(joint_category_tutorials),
        )

        self.assertEqual(
            list(joint_category_tutorials), list(related_tutorials)
        )


class TutorialCommentQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        active_confirmed: list[TutorialComment] = baker.make_recipe(
            "learning.confirmed_tutorial_comment", is_active=True, _quantity=2
        )

        active_confirmed_tutorial: Tutorial = baker.make_recipe(
            "learning.confirmed_tutorial", is_active=True
        )
        disproved_tutorial: Tutorial = baker.make_recipe(
            "learning.disproved_tutorial"
        )

        baker.make_recipe(
            "learning.tutorial_comment",
            tutorial=random.choice(
                [active_confirmed_tutorial, disproved_tutorial]
            ),
            _quantity=5,
        )

        cls.active_confirmed_comments = active_confirmed
        cls.active_confirmed_tutorial = active_confirmed_tutorial
        cls.comments_qs = TutorialComment.objects.all()

    def test_used_by_model(self):
        """Should be used as TutorialComment model's manager."""
        self.assertIsInstance(self.comments_qs, TutorialCommentQueryset)

    def test_active_and_confirmed_comments(self):
        """active_and_confirmed_comments should return queryset of active
        and confirmed tutorial comments.
        """
        active_confirmed_qs = (
            self.comments_qs.active_and_confirmed_comments().order_by()
        )
        self.assertEqual(
            list(active_confirmed_qs), list(self.active_confirmed_comments)
        )

    def test_active_confirmed_tutorials(self):
        """active_confirmed_tutorials should return comments with
        active and confirmed tutorials.
        """
        comments_active_confirmed_tutorial = list(
            self.comments_qs.active_confirmed_tutorials()
        )
        self.assertEqual(
            comments_active_confirmed_tutorial,
            list(self.active_confirmed_tutorial.comments.all()),
        )
