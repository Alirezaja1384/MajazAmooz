"""Learning views' integration tests"""
from unittest import mock
from django.test import TestCase
from django.shortcuts import reverse
from model_bakery import baker
from learning.views import home
from learning.models import Tutorial, TutorialLike


class ConstanceConfigMock:
    LEARNING_HOME_CAROUSEL_ITEMS_COUNT = 4


@mock.patch.object(home, "config", ConstanceConfigMock)
class HomeViewTest(TestCase):
    context_carousels = [
        "latest_published_tutorials",
        "most_liked_tutorials",
    ]

    def setUp(self):
        self.response = self.client.get(reverse("learning:home"))

    @classmethod
    def setUpTestData(cls):
        tutorials: list[Tutorial] = baker.make_recipe(
            "learning.confirmed_tutorial",
            is_active=True,
            # Make 1 more than carousels' item count
            _quantity=ConstanceConfigMock.LEARNING_HOME_CAROUSEL_ITEMS_COUNT
            + 1,
        )

        cls.tutorials = tutorials

    def test_status_200(self):
        """Response's status code should be 200."""
        self.assertEqual(self.response.status_code, 200)

    def test_carousels_count(self):
        """All carousels' items count should be equal to
        config's LEARNING_HOME_CAROUSEL_ITEMS_COUNT.
        """
        for carousel in self.context_carousels:
            self.assertEqual(
                len(self.response.context[carousel]),
                ConstanceConfigMock.LEARNING_HOME_CAROUSEL_ITEMS_COUNT,
            )

    def test_latest_published_tutorials(self):
        """latest_published_tutorials should order tutorials
        by their create date descendingly.
        """
        view_latest_tutorials: list[Tutorial] = list(
            self.response.context["latest_published_tutorials"]
        )
        # Reverse created tutorials and take as view_latest_tutorials length
        latest_tutorials = self.tutorials[::-1][: len(view_latest_tutorials)]

        self.assertEqual(view_latest_tutorials, latest_tutorials)

    def test_most_liked_tutorials(self):
        """most_liked_tutorials should order tutorials by their
        like count and create_date (second priority) descendingly.
        """
        baker.make(TutorialLike, tutorial=self.tutorials[0], _quantity=1)
        baker.make(TutorialLike, tutorial=self.tutorials[1], _quantity=2)

        # Re-send request to refresh response
        self.setUp()

        view_most_liked_tutorials: list[Tutorial] = list(
            self.response.context["most_liked_tutorials"]
        )

        most_liked_tutorials = [
            self.tutorials.pop(1),  # Has 2 likes
            self.tutorials.pop(0),  # Has 1 likes
        ] + self.tutorials[::-1][
            : len(view_most_liked_tutorials) - 2
        ]  # Order other tutorials by create time

        self.assertEqual(view_most_liked_tutorials, most_liked_tutorials)
