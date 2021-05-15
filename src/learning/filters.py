import django_filters
from django.db.models import Q, QuerySet


class TutorialArchiveFilterSet(django_filters.FilterSet):
    """FilterSet for tutorial archive page

    Filters:
        category: Tutorial's category slug
        search: Search condition to search in title, body and more ...
        order_by: Tutorials ordering. (choices: title, user_views_count, likes_count, create_date)
    """

    category = django_filters.CharFilter(
        field_name='categories', lookup_expr='slug')

    search = django_filters.CharFilter(method='search_filter')

    order_by = django_filters.OrderingFilter(
        fields=('title', 'user_views_count', 'likes_count', 'create_date')
    )


    def search_filter(self, queryset: QuerySet, _, value):
        """ Search condition in title, body and more ... """
        return queryset.filter(
            Q(title__contains=value) | Q(short_description__contains=value) |
            Q(body__contains=value) | Q(slug__contains=value) |
            (Q(categories__name__contains=value) & Q(categories__is_active=True)) |
            Q(tags__title__contains=value)
        )


    @property
    def qs(self):
        query_set = super().qs

        # Get ascending_or_descending from data with default value=descending
        ascending_or_descending = self.data.get('ascending_or_descending', 'descending')

        # If ascending_or_descending was descending reverse queryset
        if ascending_or_descending=='descending':
            query_set = query_set.reverse()

        return query_set
