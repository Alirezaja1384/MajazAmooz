""" QuerySet for tutorial model """
from __future__ import annotations
from django.db.models import QuerySet, Count, Q
from shared.models import ConfirmStatusChoices


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
