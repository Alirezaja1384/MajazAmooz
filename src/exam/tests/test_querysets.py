import random
from model_bakery import baker
from django.test import TestCase
from django.db.models import QuerySet
from shared.models import AnswerStatusChoices
from exam.models import ParticipantAnswer
from exam.querysets import ParticipantAnswerQuerySet


class ParticipantAnswerQuerysetTest(TestCase):
    model = ParticipantAnswer
    queryset = ParticipantAnswerQuerySet
    baker_recipe = "exam.participant_answer"

    @classmethod
    def setUpTestData(cls):
        # Using sets to avoid isEqual() issues
        cls.incorrect_answers: ParticipantAnswer = set(
            baker.make_recipe(
                cls.baker_recipe,
                correct_answer=1,
                participant_answer=2,
                _quantity=random.randint(1, 3),
            )
        )
        cls.blank_answers: ParticipantAnswer = set(
            baker.make_recipe(
                cls.baker_recipe,
                correct_answer=3,
                participant_answer=None,
                _quantity=random.randint(1, 3),
            )
        )
        cls.correct_answers: ParticipantAnswer = set(
            baker.make_recipe(
                cls.baker_recipe,
                correct_answer=4,
                participant_answer=4,
                _quantity=random.randint(1, 3),
            )
        )

        # Statuses must be set after all answers have been created.
        cls.model.objects.set_answers_status()
        cls.model.objects.all().set_answers_status()

    def get_bad_assigned_statuses(
        self, qs: QuerySet, correct_status: AnswerStatusChoices
    ):
        return list(qs.exclude(answer_status=correct_status))

    def test_get_correct_answers(self):
        """Test that get_correct_answers returns only correct answers."""
        filtered_objs = set(self.model.objects.get_correct_answers())
        self.assertEqual(self.correct_answers, filtered_objs)

    def test_get_incorrect_answers(self):
        """Test that get_incorrect_answers returns only incorrect
        answers."""
        filtered_objs = set(self.model.objects.get_incorrect_answers())
        self.assertEqual(self.incorrect_answers, filtered_objs)

    def test_get_blank_answers(self):
        """Test that get_blank_answers returns only blank answers."""
        filtered_objs = set(self.model.objects.get_blank_answers())
        self.assertEqual(self.blank_answers, filtered_objs)

    def test_set_answers_status_correct_ones(self):
        """Test that set_answers_status sets correct answers' status
        correctly.
        Note: set_answers_status() has already been called in setUpTestData().
        """
        self.assertEqual(
            self.get_bad_assigned_statuses(
                self.model.objects.get_correct_answers(),
                AnswerStatusChoices.CORRECT,
            ),
            [],
        )

    def test_set_answers_status_incorrect_ones(self):
        """Test that set_answers_status sets incorrect answers' status
        correctly.
        Note: set_answers_status() has already been called in setUpTestData().
        """
        self.assertEqual(
            self.get_bad_assigned_statuses(
                self.model.objects.get_incorrect_answers(),
                AnswerStatusChoices.INCORRECT,
            ),
            [],
        )

    def test_set_answers_status_blank_ones(self):
        """Test that set_answers_status sets blank answers' status
        correctly.
        Note: set_answers_status() has already been called in setUpTestData().
        """
        self.assertEqual(
            self.get_bad_assigned_statuses(
                self.model.objects.get_blank_answers(),
                AnswerStatusChoices.BLANK,
            ),
            [],
        )
