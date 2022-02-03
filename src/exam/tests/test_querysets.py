import random
from unittest import mock
from decimal import Decimal
from typing import Optional, Tuple, Union
from model_bakery import baker
from django.test import TestCase
from django.utils import timezone
from django.db.models import QuerySet, F
from shared.models import AnswerStatusChoices
from exam.querysets import (
    ParticipantAnswerQuerySet,
)
from exam.models import (
    ParticipantAnswer,
    ExamParticipation,
    Question,
)
from shared.models.choices import ExamParticipationStatusChoices


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


class ExamParticipationQuerySetTest(TestCase):
    """Test the ExamParticipationQuerySet."""

    correct_coin = 4
    blank_score = 1
    correct_score = 3
    incorrect_score = -1
    questions_count = 10

    @classmethod
    def setUpTestData(cls):
        cls.exam = baker.make_recipe(
            "exam.exam",
            correct_coin=cls.correct_coin,
            blank_score=cls.blank_score,
            correct_score=cls.correct_score,
            incorrect_score=cls.incorrect_score,
        )
        cls.questions = baker.make_recipe(
            "exam.question", exam=cls.exam, _quantity=cls.questions_count
        )
        cls.exam_participations: list[ExamParticipation] = baker.make_recipe(
            "exam.exam_participation",
            _fill_optional=True,
            exam=cls.exam,
            _quantity=random.randint(3, 10),
        )

    @staticmethod
    def generate_answer_choice(
        question: Question, answer_status: Tuple[int, str]
    ) -> Optional[int]:
        """Generates an answer choice for given question that will
        result in the given answer status on marking.
        """
        if answer_status == AnswerStatusChoices.BLANK:
            return None
        elif answer_status == AnswerStatusChoices.CORRECT:
            return question.correct_choice
        else:
            available_answers = [1, 2, 3, 4]
            available_answers.remove(question.correct_choice)
            return random.choice(available_answers)

    @classmethod
    def generate_participant_answers(
        cls, exam_participation: ExamParticipation
    ) -> dict[Tuple[int, str], int]:
        """Generates participant answer for each question of the
        given exam_participation.exam's questions.

        Returns:
            dict[Tuple[int, str], int]: Count of answer statuses for each
                answer status.
        """
        questions: list[Question] = list(
            exam_participation.exam.questions.all()
        )
        status_choices_count = {
            AnswerStatusChoices.BLANK: 0,
            AnswerStatusChoices.CORRECT: 0,
            AnswerStatusChoices.INCORRECT: 0,
        }
        status_choices: list = list(status_choices_count.keys())

        participant_answers = []
        for index, question in enumerate(questions):
            status = status_choices[index % len(status_choices)]
            status_choices_count[status] += 1

            participant_answers.append(
                baker.prepare_recipe(
                    "exam.participant_answer",
                    question=question,
                    exam_participation=exam_participation,
                    participant_answer=cls.generate_answer_choice(
                        question, status
                    ),
                )
            )

        ParticipantAnswer.objects.bulk_create(participant_answers)
        return status_choices_count

    @staticmethod
    def mark_exam_participation(
        exam_participation: ExamParticipation, commit=True, set_statuses=True
    ) -> ExamParticipation:
        """Marks given exam result by calling queryset's mark_participation_result
        method.
        """
        if commit:
            ExamParticipation.objects.mark_participation_result(
                exam_participation, commit=True, set_statuses=set_statuses
            )
            exam_participation.refresh_from_db()
            return exam_participation
        else:
            return ExamParticipation.objects.mark_participation_result(
                exam_participation, commit=False, set_statuses=set_statuses
            )

    @staticmethod
    def calculate_score(status_counts: dict[Tuple[int, str], int]) -> int:
        """Calculates score for the given status_counts.

        Args:
            status_counts: dict[Tuple[int, str], int]: Count of answer statuses
                for each answer status.

        Returns:
            int: Calculated score.
        """
        return (
            status_counts[AnswerStatusChoices.CORRECT]
            * ExamParticipationQuerySetTest.correct_score
            + status_counts[AnswerStatusChoices.INCORRECT]
            * ExamParticipationQuerySetTest.incorrect_score
            + status_counts[AnswerStatusChoices.BLANK]
            * ExamParticipationQuerySetTest.blank_score
        )

    def test_get_finalized(self):
        """Test that get_finalized returns only finalized exam results."""
        self.assertEqual(
            list(
                # Bad data
                ExamParticipation.objects.get_finalized().exclude(
                    is_finalized=True
                )
            ),
            [],
        )

    def test_get_in_progress(self):
        """Test that get_finalized returns only unfinished exam results."""
        self.assertEqual(
            list(
                # Bad data
                ExamParticipation.objects.get_in_progress().exclude(
                    is_finalized=False
                )
            ),
            [],
        )

    def test_get_deadline_expired(self):
        """Test that get_deadline_expired returns only exam results
        with expired deadlines."""
        self.assertEqual(
            list(
                # Bad data
                ExamParticipation.objects.get_deadline_expired().exclude(
                    deadline__lt=timezone.now()
                )
            ),
            [],
        )

    def test_mark_participation_result_status_counts(self):
        """Test that mark_participation_result sets the total_correct,
        total_incorrect and total_blank correctly.
        """
        random_participation = random.choice(self.exam_participations)
        status_counts = self.generate_participant_answers(random_participation)
        self.mark_exam_participation(random_participation)

        self.assertEqual(
            random_participation.total_correct,
            status_counts[AnswerStatusChoices.CORRECT],
        )
        self.assertEqual(
            random_participation.total_incorrect,
            status_counts[AnswerStatusChoices.INCORRECT],
        )
        self.assertEqual(
            random_participation.total_blank,
            status_counts[AnswerStatusChoices.BLANK],
        )

    def test_mark_participation_result_score_earned(self):
        """Test that mark_participation_result() sets score_earned
        correctly.
        """
        random_participation = random.choice(self.exam_participations)
        status_counts = self.generate_participant_answers(random_participation)
        self.mark_exam_participation(random_participation)

        self.assertEqual(
            self.calculate_score(status_counts),
            random_participation.score_earned,
        )

    def test_mark_participation_result_score_max(self):
        """Test that mark_participation_result() sets score_max
        correctly.
        """
        # Max score calculation doesn't depend on user's answers.
        marked_random_participation = self.mark_exam_participation(
            random.choice(self.exam_participations)
        )

        self.assertEqual(
            self.questions_count * self.correct_score,
            marked_random_participation.score_max,
        )

    def test_mark_participation_result_score_percent(self):
        """Test that mark_participation_result() sets score_percent
        correctly.
        """
        random_participation = random.choice(self.exam_participations)
        status_counts = self.generate_participant_answers(random_participation)
        self.mark_exam_participation(random_participation)

        expected_score_percent = round(
            Decimal(
                (
                    self.calculate_score(status_counts)
                    / (self.questions_count * self.correct_score)
                )
                * 100,
            ),
            2,
        )

        self.assertEqual(
            expected_score_percent,
            random_participation.score_percent,
        )

    def test_mark_participation_result_coin_earned(self):
        """Test that mark_participation_result() sets coin_earned
        correctly.
        """
        random_participation = random.choice(self.exam_participations)
        status_counts = self.generate_participant_answers(random_participation)
        self.mark_exam_participation(random_participation)

        self.assertEqual(
            random_participation.coin_earned,
            status_counts[AnswerStatusChoices.CORRECT] * self.correct_coin,
        )

    def test_mark_participation_result_update_status(self):
        """Test that mark_participation_result() updates mark_status and
        is_finalized fields.
        """
        participation = self.mark_exam_participation(
            random.choice(self.exam_participations),
            commit=False,
            set_statuses=False,
        )

        self.assertTrue(participation.is_finalized)
        self.assertEqual(
            participation.mark_status, ExamParticipationStatusChoices.COMPLETED
        )
