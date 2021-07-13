""" QuerySet for tutorial model """
from __future__ import annotations
from django.db.models import QuerySet, Prefetch, Count, Sum, Q
from django.db.models.functions import Coalesce
from shared.models import ConfirmStatusChoices
from shared.statistics import TutorialStatistics
from learning.models.category import Category
from learning.models.tutorial_comment import TutorialComment


class TutorialQueryset(QuerySet):
    """Tutorial queryset"""

    def active_and_confirmed_tutorials(self) -> TutorialQueryset:
        """
        Returns:
            [QuerySet]: Confirmed tutorials
        """
        return self.filter(
            is_active=True, confirm_status=ConfirmStatusChoices.CONFIRMED
        )

    def annonate_comments_count(self) -> TutorialQueryset:
        """Annonates active and confirmed comments count
        as comments_count.

        Returns:
            TutorialQueryset: Tutorials with comments_count.
        """
        return self.annotate(
            comments_count=Count(
                # Note: if distinct=False it will count comments
                # multiple times then count will go wrong
                "comments",
                distinct=True,
                filter=Q(comments__is_active=True)
                & Q(comments__confirm_status=ConfirmStatusChoices.CONFIRMED),
            ),
        )

    def only_main_fields(self) -> TutorialQueryset:
        """Only gets title, slug, short_description, likes_count
        and image from db and returns them.

        Returns:
            TutorialQueryset: Main fields of tutorials.
        """
        return self.only(
            "title", "slug", "short_description", "likes_count", "image"
        )

    def prefetch_active_categories(self) -> TutorialQueryset:
        """Prefetches active categories.

        Returns:
            TutorialQueryset: Original queryset + prefetched categories.
        """
        return self.prefetch_related(
            Prefetch(
                "categories",
                queryset=Category.objects.active_categories().select_related(
                    "parent_category"
                ),
            ),
        )

    def prefetch_active_confirmed_comments(self) -> TutorialQueryset:
        """Prefetches active and confirmed comments.

        Returns:
            TutorialQueryset: Original queryset + prefetched comments.
        """
        return self.prefetch_related(
            Prefetch(
                "comments",
                queryset=TutorialComment.objects.select_related(
                    "parent_comment", "user"
                ).active_and_confirmed_comments(),
            ),
        )

    def aggregate_statistics(self) -> TutorialStatistics:
        """Aggregates statistics contining tutorials_count,
        likes_count, views_count and comments_count.

        Returns:
            TutorialStatistics: Queryset's statistics.
        """
        statistics = self.aggregate(
            tutorials_count=Count("pk"),
            # Use Coalesce to ensure aggregation result won't be None
            likes_count=Coalesce(Sum("likes_count"), 0),
            views_count=Coalesce(Sum("user_views_count"), 0),
        )

        # TODO: change comments_count calcultion method
        statistics["comments_count"] = (
            TutorialComment.objects.filter(tutorial__in=self)
            .active_and_confirmed_comments()
            .count()
        )

        return TutorialStatistics(statistics)

    def get_related_tutorials(
        self, tutorial, tutorial_count: int = 5
    ) -> TutorialQueryset:
        """Finds related tutorials to given tutorial (by joint categories).

        Args:
            tutorial (Tutorial): Base tutorial to find related tutorials
                by its categories.

            tutorial_count (int, optional): Expected max count of tutorial.
                Defaults to 5.

        Returns:
            TutorialQueryset: Related tutorials to given one.
        """

        def _flat_categories_parents(categories: list):
            """Returns list of categories and their parents"""
            result = categories

            for category in categories:
                while category.parent_category:
                    category = category.parent_category
                    result.append(category)

            # Distinct result
            return list(dict.fromkeys(result))

        categories_and_parents = list(tutorial.categories.all())
        # If tutorial doesn't have any active category return empty
        if len(categories_and_parents) == 0:
            return self.none()

        categories = _flat_categories_parents(categories_and_parents)

        # Get tutorials with joint categories
        related_tutorials = (
            self.exclude(pk=tutorial.pk)
            .filter(categories__in=categories)
            .distinct()[:tutorial_count]
        )

        return related_tutorials
