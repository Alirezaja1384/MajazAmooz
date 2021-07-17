"""Learning views' integration tests"""
import random
from typing import Optional
from unittest import mock
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.shortcuts import reverse, resolve_url
from django.core.exceptions import MultipleObjectsReturned
from model_bakery import baker
from shared.tests.utils import prevent_request_warnings
from learning.views import home, tutorial as tutorial_details_view
from learning.models import Tutorial, TutorialLike, TutorialView


User = get_user_model()


class ConstanceConfigMock:
    TUTORIAL_VIEW_COIN = 5
    TUTORIAL_VIEW_SCORE = 4
    LEARNING_HOME_CAROUSEL_ITEMS_COUNT = 4
    LEARNING_RECOMMENDATION_ITEMS_COUNT = 5


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


@mock.patch.object(tutorial_details_view, "config", ConstanceConfigMock)
class TutorialDetailsViewTest(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client.force_login(self.user)

        self.random_active_confirmed_tutorial = random.choice(
            self.active_confirmed_tutorials
        )

    @classmethod
    def setUpTestData(cls):
        active_confirmed_tutorials: list[Tutorial] = baker.make_recipe(
            "learning.confirmed_tutorial",
            is_active=True,
            # Make 1 more than recommendation' items count
            _quantity=ConstanceConfigMock.LEARNING_RECOMMENDATION_ITEMS_COUNT
            + 1,
        )

        cls.active_confirmed_tutorials = active_confirmed_tutorials

    def get_view_response(
        self, tutorial: Optional[Tutorial] = None
    ) -> HttpResponse:
        """Generates url by given tutorial's slug and returns its response.

        Args:
            tutorial (Tutorial[Tutorial]): Tutorial to get response of
                learning:tutorial view. Defaults to None.

        Returns:
            HttpResponse: Response of view.
        """
        if not tutorial:
            tutorial = self.random_active_confirmed_tutorial

        url = resolve_url("learning:tutorial", slug=tutorial.slug)
        return self.client.get(url, follow=True)

    def record_tutorial_view(
        self, user: Optional[User] = None, tutorial: Optional[Tutorial] = None
    ):
        if not tutorial:
            tutorial = self.random_active_confirmed_tutorial

        request = RequestFactory().get("/tutorial/" + tutorial.slug)
        request.user = user or self.user

        view = tutorial_details_view.TutorialDetailsView()
        view.setup(request, slug=tutorial.slug)
        view.record_tutorial_view(tutorial)

    def test_active_confirmed_tutorial_status_200(self):
        """Response's status code should be 200."""
        # It automatically uses ana active and confirmed tutorial
        response = self.get_view_response()
        self.assertEqual(response.status_code, 200)

    @prevent_request_warnings
    def test_inactive_tutorial_status_404(self):
        """Response's status code should be 404 when tutorial
        ia inactive or disproved.
        """
        inactive_tutorial = baker.make_recipe(
            "learning.tutorial", is_active=False
        )
        response = self.get_view_response(inactive_tutorial)

        self.assertEqual(response.status_code, 404)

    @prevent_request_warnings
    def test_disproved_tutorial_status_404(self):
        """Response's status code should be 404 when tutorial
        ia inactive or disproved.
        """
        disproved_tutorial = baker.make_recipe("learning.disproved_tutorial")
        response = self.get_view_response(disproved_tutorial)

        self.assertEqual(response.status_code, 404)

    def test_cookies_csrftoken(self):
        """Should set csrftoken in user's cookies."""
        response = self.get_view_response()
        self.assertIn("csrftoken", response.client.cookies)

    def test_context_tutorial_join_relations(self):
        """Tutorial object should join author (user table)."""
        should_join = ["author"]
        context_tutorial: Tutorial = self.get_view_response().context[
            "tutorial"
        ]

        for rel in should_join:
            self.assertIn(
                rel,
                context_tutorial._state.fields_cache,
                f"{rel} has not been joined. Use select_related to join it.",
            )

    def test_context_tutorial_prefetch_relations(self):
        """Tutorial object should prefetch categories, comments and tags."""
        should_prefeth = ["categories", "comments", "tags"]

        context_tutorial: Tutorial = self.get_view_response().context[
            "tutorial"
        ]

        for rel in should_prefeth:
            self.assertIn(
                rel,
                context_tutorial._prefetched_objects_cache,
                f"{rel} has not been prefetched. Use prefetch_related.",
            )

    def test_liked_by_current_user_liked(self):
        """Context's liked_by_current_user should be True if tutorial
        liked by user.
        """
        baker.make(
            TutorialLike,
            user=self.user,
            tutorial=self.random_active_confirmed_tutorial,
        )
        liked_by_current_user = self.get_view_response().context[
            "liked_by_current_user"
        ]

        self.assertTrue(liked_by_current_user)

    def test_liked_by_current_user_not_liked(self):
        """Context's liked_by_current_user should be False if tutorial
        is not liked by user.
        """
        liked_by_current_user = self.get_view_response().context[
            "liked_by_current_user"
        ]

        self.assertFalse(liked_by_current_user)

    def test_recommendation_items_count(self):
        """Maximum count of recommended items should be
        config.LEARNING_RECOMMENDATION_ITEMS_COUNT.
        """
        context = self.get_view_response().context
        recommendations = [
            context[rec]
            for rec in [
                "related_tutorials",
                "latest_tutorials",
                "most_popular_tutorials",
            ]
        ]

        for rec in recommendations:
            self.assertLessEqual(
                len(rec),
                ConstanceConfigMock.LEARNING_RECOMMENDATION_ITEMS_COUNT,
            )

    @mock.patch.object(
        tutorial_details_view.TutorialDetailsView,
        "record_tutorial_view",
        mock.DEFAULT,
    )
    def test_call_record_tutorial_view(self, record_tutorial_view_mock):
        """Tutorial view should call record_tutorial_view method."""
        self.get_view_response()

        self.assertTrue(
            record_tutorial_view_mock.called,
            "TutorialDetailsView didn't call record_tutorial_view.",
        )

    def test_record_tutorial_view_insert_view_to_db(self):
        """record_tutorial_view should insert TutorialView in database
        if not exists.
        """
        self.record_tutorial_view()

        self.assertTrue(
            TutorialView.objects.filter(
                user=self.user, tutorial=self.random_active_confirmed_tutorial
            ).exists(),
            "record_tutorial_view didn't insert TutorialView to database.",
        )

    def test_record_tutorial_view_insert_once(self):
        """record_tutorial_view should insert just once."""
        self.record_tutorial_view()
        self.record_tutorial_view()

        try:
            TutorialView.objects.get(
                user=self.user, tutorial=self.random_active_confirmed_tutorial
            )
        except MultipleObjectsReturned:
            self.fail(
                "record_tutorial_view inserted TutorialView multiple times."
            )

    def test_record_tutorial_view_score_coin_use_config(self):
        """Inserted TutorialView object's score and coin should be equal
        to config's TUTORIAL_VIEW_COIN and TUTORIAL_VIEW_SCORE.
        """
        self.record_tutorial_view()

        tutorial_view: TutorialView = TutorialView.objects.get(
            user=self.user, tutorial=self.random_active_confirmed_tutorial
        )

        self.assertEqual(
            tutorial_view.score, ConstanceConfigMock.TUTORIAL_VIEW_SCORE
        )
        self.assertEqual(
            tutorial_view.coin, ConstanceConfigMock.TUTORIAL_VIEW_COIN
        )
