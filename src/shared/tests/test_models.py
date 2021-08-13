import random
from unittest import mock
from shared.models import AbstractScoreCoinModel
from .utils import ModelTestCase


class AbstractScoreCoinModelTest(ModelTestCase):
    class TestScoreCoinModel(AbstractScoreCoinModel):
        class Meta:
            managed = False

    model = TestScoreCoinModel

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
        obj = self.model.objects.create(score=expected_score + 1)

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
        obj = self.model.objects.create(coin=expected_coin + 1)

        self.assertEqual(obj.coin, expected_coin)
