import random
from unittest import mock
from typing import Tuple, Union
from model_bakery import baker
from django.test import TestCase
from django.db.models import QuerySet, F
from shared.models import AnswerStatusChoices
from exam.querysets import ParticipantAnswerQuerySet
from exam.models import ParticipantAnswer, Question


class ParticipantAnswerQuerysetTest(TestCase):
    model = ParticipantAnswer
    queryset = ParticipantAnswerQuerySet
    baker_recipe = "exam.participant_answer"

    @classmethod
    def setUpTestData(cls):
        question: Question = baker.make_recipe(
            "exam.question", correct_choice=4
        )

        # * Using sets to avoid isEqual() issues
        cls.incorrect_answer_pks: set[int] = set(
            [
                obj.pk
                for obj in baker.make_recipe(
                    cls.baker_recipe,
                    question=question,
                    participant_answer=2,
                    _quantity=random.randint(1, 3),
                )
            ]
        )
        cls.blank_answer_pks: set[int] = set(
            [
                obj.pk
                for obj in baker.make_recipe(
                    cls.baker_recipe,
                    question=question,
                    participant_answer=None,
                    _quantity=random.randint(1, 3),
                )
            ]
        )
        cls.correct_answer_pks: set[int] = set(
            [
                obj.pk
                for obj in baker.make_recipe(
                    cls.baker_recipe,
                    question=question,
                    participant_answer=4,
                    _quantity=random.randint(1, 3),
                )
            ]
        )

        # Statuses must be set after all answers have been created.
        cls.model.objects.set_answers_status()

    def get_wrong_assigned_status_count(
        self, qs: QuerySet, correct_status: Union[Tuple[int, str], int]
    ) -> int:
        return qs.exclude(answer_status=correct_status).count()

    def is_queryset_equal(self, qs: QuerySet, pks_set: set[int]):
        """Test that the queryset contains the correct objects."""
        self.assertEqual(set(qs.values_list("id", flat=True)), pks_set)

    def test_get_correct_answers(self):
        """Test that get_correct_answers returns only correct answers."""
        self.is_queryset_equal(
            self.model.objects.get_correct_answers(), self.correct_answer_pks
        )

    def test_get_incorrect_answers(self):
        """Test that get_incorrect_answers returns only incorrect
        answers."""
        self.is_queryset_equal(
            self.model.objects.get_incorrect_answers(),
            self.incorrect_answer_pks,
        )

    def test_get_blank_answers(self):
        """Test that get_blank_answers returns only blank answers."""
        self.is_queryset_equal(
            self.model.objects.get_blank_answers(), self.blank_answer_pks
        )

    @mock.patch.object(queryset, "set_correct_answers")
    def test_set_answers_status_calls_set_correct_answers(
        self, mock_set_currect_answers: mock.MagicMock
    ):
        """set_answer_status should call set_correct_answers().

        Args:
            mock_set_currect_answers: mock object for set_correct_answers()
        """
        self.model.objects.set_answers_status()
        self.assertTrue(mock_set_currect_answers.called)

    def test_set_answers_status_correct_ones(self):
        """Test that set_answers_status sets correct answers' status
        correctly.
        Note: set_answers_status() has already been called in setUpTestData().
        """
        self.assertEqual(
            self.get_wrong_assigned_status_count(
                self.model.objects.get_correct_answers(),
                AnswerStatusChoices.CORRECT,
            ),
            0,
        )

    def test_set_answers_status_incorrect_ones(self):
        """Test that set_answers_status sets incorrect answers' status
        correctly.
        Note: set_answers_status() has already been called in setUpTestData().
        """
        self.assertEqual(
            self.get_wrong_assigned_status_count(
                self.model.objects.get_incorrect_answers(),
                AnswerStatusChoices.INCORRECT,
            ),
            0,
        )

    def test_set_answers_status_blank_ones(self):
        """Test that set_answers_status sets blank answers' status
        correctly.
        Note: set_answers_status() has already been called in setUpTestData().
        """
        self.assertEqual(
            self.get_wrong_assigned_status_count(
                self.model.objects.get_blank_answers(),
                AnswerStatusChoices.BLANK,
            ),
            0,
        )

    def test_set_correct_answers(self):
        """Test that set_correct_answers sets correct_answer correctly."""
        self.model.objects.set_correct_answers()

        # The wrong assigned correct_answer fields should not exist.
        self.assertEqual(
            # There should not be any model object with wrong correct_answer
            self.model.objects.select_related("question")
            # Only include objects with correct_answer=None
            .only("correct_answer", "question__correct_answer")
            # Get only the objects with incorrect correct_answer field
            .exclude(correct_answer=F("question__correct_choice")).count(),
            0,
        )

    def test_aggregate_answer_statuses_count(self):
        """Test that aggregate_answer_statuses_count returns the correct
        number of answers for each status.
        """
        answer_statuses = self.model.objects.aggregate_answer_statuses_count()

        self.assertEqual(answer_statuses.blank, len(self.blank_answer_pks))
        self.assertEqual(answer_statuses.correct, len(self.correct_answer_pks))
        self.assertEqual(
            answer_statuses.incorrect, len(self.incorrect_answer_pks)
        )
