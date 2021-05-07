import django_filters
from django.db.models import Q


class TutorialArchiveFilterSet(django_filters.FilterSet):
    """FilterSet for tutorial archive page

    Filters:
        category: Tutorial's category slug
        search: Search condition to search in title, body and more ...
    """
    category = django_filters.CharFilter(
        field_name='categories', lookup_expr='slug')
    search = django_filters.CharFilter(method='search_filter')

    def search_filter(self, queryset, _, value):
        return queryset.filter(
            Q(title__contains=value) | Q(short_description__contains=value) |
            Q(body__contains=value) | Q(slug__contains=value) |
            Q(categories__name__contains=value)
        )
