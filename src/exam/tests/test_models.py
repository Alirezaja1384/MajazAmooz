from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from model_bakery import baker
from shared.models import AnswerStatusChoices
from exam.models import Exam, Question, ExamResult, ParticipantAnswer


User = get_user_model()


class ExamTest(TestCase):
    bakery_recipe = "exam.exam"

    def test_str(self):
        """Test the string representation of an exam."""
        exam: Exam = baker.make_recipe(self.bakery_recipe, title="Test Exam")
        self.assertEqual(str(exam), "Test Exam")

    def test_slug_auto_generation(self):
        """Test that the slug is automatically generated."""
        exam: Exam = baker.make_recipe(self.bakery_recipe, title="Test Exam")
        self.assertEqual(exam.slug, "test-exam")

    def test_slug_unicode_support(self):
        """Test that the automatically generated slug supports unicode."""
        exam: Exam = baker.make_recipe(self.bakery_recipe, title="آزمون تست")
        self.assertEqual(exam.slug, "آزمون-تست")


class QuestionTest(TestCase):
    bakery_recipe = "exam.question"

    def test_str(self):
        """Test the string representation of a question."""
        question: Question = baker.make_recipe(
            self.bakery_recipe, question_text="Test Question"
        )
        self.assertEqual(str(question), "Test Question")


class ExamResultTest(TestCase):
    baker_recipe = "exam.exam_result"

    @classmethod
    def setUpTestData(cls):
        """Set up the test data."""
        cls.user = baker.make(User, username="testuser")
        cls.exam = baker.make_recipe("exam.exam", title="Test Exam")
        cls.exam_result = baker.make_recipe(
            cls.baker_recipe, user=cls.user, exam=cls.exam
        )

    def test_str(self):
        """Test the string representation of a question.
        Exam result's string representation should contain the user's
        username and the exam's title.
        """
        result_str = str(self.exam_result)
        self.assertIn(self.user.username, result_str)
        self.assertIn(self.exam.title, result_str)

    def test_set_deadline_no_duration(self):
        """Test that the deadline is set to None if exam has no deadline
        duration.
        """
        exam: Exam = baker.make_recipe(
            ExamTest.bakery_recipe, deadline_duration=None
        )
        exam_result: ExamResult = baker.make_recipe(
            "exam.exam_result", exam=exam
        )

        self.assertIsNone(exam_result.deadline)

    def test_set_deadline_with_duration(self):
        """Test that the deadline is set correctly when exam has a deadline."""
        exam: Exam = baker.make_recipe(
            ExamTest.bakery_recipe, deadline_duration=timedelta(hours=1)
        )
        exam_result: ExamResult = baker.make_recipe(
            "exam.exam_result", exam=exam
        )

        self.assertEqual(
            exam_result.deadline,
            exam_result.started_at + exam.deadline_duration,
        )


class ParticipantAnswerTest(TestCase):
    """Test the ParticipantAnswer model."""

    bakery_recipe = "exam.participant_answer"

    def test_answer_status_incorrect(self):
        """Test that the answer status is set to incorrect when participant's
        answer is not the correct answer.
        """
        participant_answer: ParticipantAnswer = baker.make_recipe(
            self.bakery_recipe, participant_answer=1, correct_answer=2
        )

        self.assertEqual(
            participant_answer.answer_status, AnswerStatusChoices.INCORRECT
        )

    def test_answer_status_correct(self):
        """Test that the answer status is set to correct when participant's
        answer is the correct answer.
        """
        participant_answer: ParticipantAnswer = baker.make_recipe(
            self.bakery_recipe, participant_answer=1, correct_answer=1
        )

        self.assertEqual(
            participant_answer.answer_status, AnswerStatusChoices.CORRECT
        )

    def test_answer_status_blank(self):
        """Test that the answer status is set to blank when participant
        didn't answer the question.
        """
        participant_answer: ParticipantAnswer = baker.make_recipe(
            self.bakery_recipe, participant_answer=None, correct_answer=1
        )

        self.assertEqual(
            participant_answer.answer_status, AnswerStatusChoices.BLANK
        )
