""" QuerySet for tutorial model """
from __future__ import annotations
from django.db.models import QuerySet, Prefetch, Count, Sum, Q
from django.db.models.functions import Coalesce
from shared.models import ConfirmStatusChoices
from shared.typed_dicts import TutorialStatistics
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
        """Annonates comments count as comments_count

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

    def filter_by_categories(
        self,
        categories: list,
        tutorial_count: int = 5,
    ) -> TutorialQueryset:
        """Filters tutorials by list of categories.

        Args:
            categories (list): Categories to search tutorials by them
            tutorial_count (int, optional): Expected count of tutorial.
                Defaults to 5.

        Returns:
            TutorialQueryset: Tutorials already have given category.
        """
        return (
            self.filter(categories__in=categories)
            .order_by("-create_date")
            .active_and_confirmed_tutorials()
            .only_main_fields()
            .distinct()[:tutorial_count]
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
