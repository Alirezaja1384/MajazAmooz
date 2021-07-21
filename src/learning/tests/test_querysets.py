import random
import datetime
from typing import Type
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from model_bakery import baker
from shared.statistics import MonthlyCountStatistics
from learning.models import (
    Category,
    Tutorial,
    TutorialComment,
    TutorialLike,
    TutorialView,
    TutorialUpVote,
    TutorialDownVote,
    TutorialCommentLike,
    TutorialCommentUpVote,
    TutorialCommentDownVote,
)
from learning.models.tutorial_user_relation_models import (
    AbstractTutorialScoreCoinModel,
)
from learning.models.tutorial_comment_user_relation_models import (
    AbstractCommentScoreCoinModel,
)
from learning.querysets.category_queryset import CategoryQueryset
from learning.querysets.tutorial_queryset import TutorialQueryset
from learning.querysets.tutorial_comment_queryset import (
    TutorialCommentQueryset,
)
from learning.querysets.tutorial_user_relation_querysets import (
    TutorialUserRelationQueryset,
)
from learning.querysets.tutorial_comment_user_relation_querysets import (
    TutorialCommentUserRelationQueryset,
)

User = get_user_model()


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
            "learning.disproved_tutorial",
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
        active_confirmed_tutorial: Tutorial = baker.make_recipe(
            "learning.confirmed_tutorial", is_active=True
        )
        disproved_tutorial: Tutorial = baker.make_recipe(
            "learning.disproved_tutorial"
        )

        active_confirmed = baker.make_recipe(
            "learning.confirmed_tutorial_comment",
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


class TutorialUserRelationQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        all_models: list[Type[AbstractTutorialScoreCoinModel]] = [
            TutorialLike,
            TutorialView,
            TutorialUpVote,
            TutorialDownVote,
        ]
        model = random.choice(all_models)

        # date, count
        date_counts = [
            # 4th jalali month (Khordad)
            (datetime.datetime(2021, 6, 10), 3),
            # 3rd jalali month (Tir)
            (datetime.datetime(2021, 7, 10), 2),
        ]

        tutorial = baker.make_recipe("learning.tutorial")
        for date_count in date_counts:
            month_items = baker.make(
                model,
                tutorial=tutorial,
                _quantity=date_count[1],
            )
            for item in month_items:
                # create_date has auto_now_add=True, then
                # its create_date can only change on update.
                item.create_date = timezone.make_aware(date_count[0])
                item.save()

        cls.all_models = all_models
        cls.queryset = model.objects.all()

    def test_used_by_all_models(self):
        """Should be used as all models' manager."""
        for model in self.all_models:
            qs = model.objects.all()
            self.assertIsInstance(qs, TutorialUserRelationQueryset)

    def test_get_last_months_count_statistics(self):
        """get_last_months_count_statistics should return last months
        label and object counts created in each month.
        """
        today = datetime.date(2021, 7, 14)
        statistics = list(
            self.queryset.get_last_months_count_statistics(2, today)
        )
        expected_statistics = [
            MonthlyCountStatistics({"label": "خرداد 1400", "count": 3}),
            MonthlyCountStatistics({"label": "تیر 1400", "count": 2}),
        ]
        self.assertEqual(statistics, expected_statistics)


class TutorialCommentUserRelationQuerysetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        all_models: list[Type[AbstractCommentScoreCoinModel]] = [
            TutorialCommentLike,
            TutorialCommentUpVote,
            TutorialCommentDownVote,
        ]
        model = random.choice(all_models)

        active_confirmed_comment = baker.make_recipe(
            "learning.confirmed_tutorial_comment"
        )
        disproved_comment = baker.make_recipe(
            "learning.disproved_tutorial_comment"
        )

        baker.make(
            model,
            comment=random.choice(
                [active_confirmed_comment, disproved_comment]
            ),
            _quantity=5,
        )

        cls.model = model
        cls.all_models = all_models
        cls.queryset = model.objects.all()
        cls.active_confirmed_comment = active_confirmed_comment

    def test_used_by_all_models(self):
        """Should be used as all models' manager."""
        for model in self.all_models:
            qs = model.objects.all()
            self.assertIsInstance(qs, TutorialCommentUserRelationQueryset)

    def test_active_confirmed_comments(self):
        """Should return objects that have active and
        confirmed comment."""
        objs_active_confirmed_comment = (
            self.queryset.active_confirmed_comments()
        )
        self.assertEqual(
            list(objs_active_confirmed_comment),
            list(
                self.model.objects.filter(
                    comment=self.active_confirmed_comment
                )
            ),
        )
