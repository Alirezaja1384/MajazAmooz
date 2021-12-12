import random
from copy import deepcopy
from unittest import mock
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from model_bakery import baker
from shared.models import AbstractScoreCoinModel
from .utils import ModelTestCase


USER_MODEL = get_user_model()


class AbstractScoreCoinModelTest(ModelTestCase):
    class TestTutorialLikeModel(AbstractScoreCoinModel):
        user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
        tutorial = models.ForeignKey(
            "learning.Tutorial", on_delete=models.CASCADE
        )

        # Settings
        user_relation_field = "user"
        object_relation_field = "tutorial"
        object_relation_count_field_name = "likes_count"

        class Meta:
            managed = False

        def get_create_score(self):
            return random.randint(1, 10)

        def get_create_coin(self):
            return random.randint(1, 10)

    model = TestTutorialLikeModel

    @classmethod
    def setUpTestData(cls):
        cls.tutorial: models.Model = deepcopy(
            baker.make_recipe("learning.tutorial")
        )
        cls.user: models.Model = deepcopy(baker.make(USER_MODEL))

        # Note: These two objects are not real ones
        #       They're only copies of the real ones.
        # Why? Because AbstractScoreCoinModel's internal
        #      methods will change the real objects.
        cls.tutorial_copy = deepcopy(cls.tutorial)
        cls.user_copy = deepcopy(cls.user)

        cls.model_instance: cls.TestTutorialLikeModel = baker.make(
            cls.model, user=cls.user, tutorial=cls.tutorial
        )

    def make_model_instance(self, **kwargs) -> TestTutorialLikeModel:
        return baker.make(
            self.model, user=self.user, tutorial=self.tutorial, **kwargs
        )

    @mock.patch.object(
        model, "get_create_score", return_value=random.randint(1, 5)
    )
    def test_automatically_set_score(
        self, get_create_score_mock: mock.MagicMock
    ):
        """Should ignore given score and set get_create_score's return
        value as object's score.

        Args:
            get_create_score_mock (mock.MagicMock): Mocked
                get_create_score method.
        """
        expected_score = get_create_score_mock()
        obj = self.make_model_instance(score=expected_score + 1)

        self.assertEqual(obj.score, expected_score)

    @mock.patch.object(
        model, "get_create_coin", return_value=random.randint(1, 5)
    )
    def test_automatically_set_coin(
        self, get_create_coin_mock: mock.MagicMock
    ):
        """Should ignore given coin and set get_create_coin's return
        value as object's coin.

        Args:
            get_create_coin_mock (mock.MagicMock): Mocked
                get_create_coin method.
        """
        expected_coin = get_create_coin_mock()
        obj = self.make_model_instance(coin=expected_coin + 1)

        self.assertEqual(obj.coin, expected_coin)

    def test_increase_user_score_coin(self):
        """Test that automatically increases user's score and
        coin on create.
        """
        old_scores = self.user_copy.scores
        old_coins = self.user_copy.coins

        self.assertEqual(
            self.user.scores, old_scores + self.model_instance.score
        )
        self.assertEqual(self.user.coins, old_coins + self.model_instance.coin)

    def test_decrease_user_score_coin(self):
        """Test that automatically decreases user's score and
        coin on delete.
        """
        user_before_delete = deepcopy(self.user)
        instance_copy = deepcopy(self.model_instance)

        self.model_instance.delete()

        self.assertEqual(
            self.user.scores, user_before_delete.scores - instance_copy.score
        )
        self.assertEqual(
            self.user.coins, user_before_delete.coins - instance_copy.coin
        )

    def test_invalid_settings(self):
        """Test that raises ImproperlyConfigured if user_relation_field,
        object_relation_field or object_relation_count_field_name is Invalid.
        """
        invalid_settings = [
            {"user_relation_field": [1, 2]},
            {"user_relation_field": "user_invalid"},
            {"object_relation_field": [1, 2]},
            {"object_relation_field": "tutorial_invalid"},
            {"object_relation_count_field_name": [1, 2]},
            {"object_relation_count_field_name": "likes_count_invalid"},
        ]

        for setting in invalid_settings:
            for setting_name, setting_value in setting.items():
                # Set invalid setting
                with mock.patch.object(
                    self.model, setting_name, new=setting_value
                ):
                    # Should raise ImproperlyConfigured
                    with self.assertRaises(ImproperlyConfigured):
                        self.make_model_instance()

    def test_refresh_user_score_coin(self):
        """Test that calls model object user's refresh_from_db method."""
        with mock.patch.object(self.user, "refresh_from_db") as mock_refresh:
            self.make_model_instance()

            # Mocked refresh_from_db method should have been called
            self.assertTrue(mock_refresh.called)

    def test_refresh_tutorial_likes_count(self):
        """Test that calls tutorial's refresh_from_db method."""
        with mock.patch.object(
            self.tutorial, "refresh_from_db"
        ) as mock_refresh:
            self.make_model_instance()

            # Mocked refresh_from_db method should have been called
            self.assertTrue(mock_refresh.called)

    def test_nested_user_relation(self):
        """Test that user_relation_field can be a nested field."""
        with mock.patch.object(
            self.model, "user_relation_field", new="tutorial.author"
        ):
            old_scores = self.tutorial.author.scores
            old_coins = self.tutorial.author.coins

            instance = self.make_model_instance()

            self.assertEqual(
                self.tutorial.author.scores,
                old_scores + instance.score,
            )
            self.assertEqual(
                self.tutorial.author.coins,
                old_coins + instance.coin,
            )
