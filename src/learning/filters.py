import django_filters
from django.db.models import Q, QuerySet


class AscendingDescendingChoices:
    ASCENDING = "ascending"
    DESCENDING = "descending"


class TutorialArchiveFilterSet(django_filters.FilterSet):
    """FilterSet for tutorial archive page.

    Filters:
        category: Tutorial's category slug.
        search: Search condition to search in title, body and more ...
        order_by: Tutorials ordering. (choices: title, user_views_count,
            likes_count, create_date).
        ascending_or_descending: Overrides ascending/descending order of
            order_by filter.
    """

    DEFAULT_ORDER_BY = "-create_date"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make data mutable if it's immutable
        self.data = self.data.copy()

        # Set default order_by
        if "order_by" not in self.data:
            self.data["order_by"] = self.DEFAULT_ORDER_BY

        # Get ordering value
        ordering: str = self.data["order_by"]
        # Get ascending_or_descending from data with default value=descending
        ascending_or_descending = self.data.get("ascending_or_descending")

        # If ascending_or_descending was descending and order_by didn't have
        # '-' at the start, add it.
        if (
            ascending_or_descending == AscendingDescendingChoices.DESCENDING
            and (not ordering.startswith("-"))
        ):
            self.data["order_by"] = "-" + ordering

        # If ascending_or_descending was ascending and order_by had
        # '-' at the start, remove it.
        if (
            ascending_or_descending == AscendingDescendingChoices.ASCENDING
            and (ordering.startswith("-"))
        ):
            self.data["order_by"] = ordering[1:]

    category = django_filters.CharFilter(
        field_name="categories", lookup_expr="slug"
    )

    search = django_filters.CharFilter(method="search_filter")

    order_by = django_filters.OrderingFilter(
        fields=("title", "user_views_count", "likes_count", "create_date"),
    )

    def search_filter(self, queryset: QuerySet, _, value):
        """Search condition in title, body and more ..."""
        return queryset.filter(
            Q(title__contains=value)
            | Q(short_description__contains=value)
            | Q(body__contains=value)
            | Q(slug__contains=value)
            | (
                Q(categories__name__contains=value)
                & Q(categories__is_active=True)
            )
            | Q(tags__title__contains=value)
        )
