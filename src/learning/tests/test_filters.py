import random
from typing import Tuple
from model_bakery import baker
from django.db.models import QuerySet
from django.test import TestCase, RequestFactory
from learning.models import Tutorial, Category, TutorialTag
from learning.filters import (
    TutorialArchiveFilterSet,
    AscendingDescendingChoices,
)


class TutorialArchiveFilterSetTest(TestCase):
    filter_set = TutorialArchiveFilterSet

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        baker.make_recipe("learning.tutorial", _quantity=3)
        cls.queryset = Tutorial.objects.all()

    def _get_filterset(self, **kwargs) -> QuerySet:
        """Filters queryset and returns the new queryset. Passes
            any keyword argument as filter data to filterset.

        Returns:
            QuerySet: Filtered queryset.
        """
        request = self.factory.get("/", data=kwargs)
        filter_set = self.filter_set(request.GET, self.queryset)

        return filter_set

    def _get_ordering_choices(self) -> Tuple[str, str]:
        """Ordering choices for order_by filters

        Returns:
            Tuple[str, str]: First index is ordering value
                and second on is its name.
        """
        return self._get_filterset().filters["order_by"].extra["choices"]

    def test_category_filter(self):
        """category filter should filter tutorials by their categories."""
        category: Category = baker.make_recipe("learning.active_category")
        cat_tutorials: list[Tutorial] = baker.make_recipe(
            "learning.confirmed_tutorial",
            is_active=True,
            categories=[category],
            _quantity=2,
        )
        qs = self._get_filterset(category=category.slug).qs.order_by()

        self.assertEqual(cat_tutorials, list(qs))

    def test_order_by_filter(self):
        """order_by filter should order tutorials by given ordering."""
        order_choices = self._get_ordering_choices()

        for ordering in order_choices:
            filter_set = self._get_filterset(order_by=ordering[0])
            qs_ordering = filter_set.qs.query.order_by

            self.assertEqual(
                qs_ordering,
                (ordering[0],),
                f"{ordering[1]} ordering didn't apply correctly",
            )

    def test_ascending_or_descending_override_order_by(self):
        """ascending_or_descending filter should override
        ascending/descending order of tutorials.
        """
        order_choices = self._get_ordering_choices()

        for ordering in order_choices:
            if ordering[0].startswith("-"):
                # If original ordering is descending
                opposite_asc_desc = AscendingDescendingChoices.ASCENDING
                opposite_ordering = ordering[0][1:]
            else:
                # If original ordering is ascending
                opposite_asc_desc = AscendingDescendingChoices.DESCENDING
                opposite_ordering = "-" + ordering[0]

            filter_set = self._get_filterset(
                order_by=ordering[0], ascending_or_descending=opposite_asc_desc
            )
            qs_ordering = filter_set.qs.query.order_by

            self.assertEqual(qs_ordering, (opposite_ordering,))

    def test_search_tutorial_fields(self):
        """search filter should search in tutorials by "title",
        "short_description", "body" and "slug" fields.
        """
        search_fields = ["title", "short_description", "body", "slug"]
        random_tutorial = random.choice(self.queryset)

        for field in search_fields:
            field_val = getattr(random_tutorial, field)
            qs = self._get_filterset(search=field_val).qs

            self.assertEqual([random_tutorial], list(qs))

    def test_search_tutorial_category_name(self):
        """search filter should search in tutorials' categories names."""
        category: Category = baker.make_recipe("learning.active_category")
        cat_tutorials: list[Tutorial] = baker.make_recipe(
            "learning.confirmed_tutorial",
            is_active=True,
            categories=[category],
            _quantity=2,
        )

        qs = self._get_filterset(search=category.name).qs.order_by("pk")

        self.assertEqual(cat_tutorials, list(qs))

    def test_search_tutorial_tag_title(self):
        """search filter should search in tutorials' tags title."""
        tag: TutorialTag = baker.make(
            TutorialTag,
            tutorial=baker.make_recipe(
                "learning.confirmed_tutorial", is_active=True
            ),
        )

        qs = self._get_filterset(search=tag.title).qs

        self.assertEqual([tag.tutorial], list(qs))
