from datetime import timedelta
from constance import config
from model_bakery import baker
from django.test import TestCase
from django.forms import ValidationError
from django.contrib.auth import get_user_model
from exam.querysets import ParticipantAnswerQuerySet
from exam.models import Exam, Question, ExamParticipation, ParticipantAnswer


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


class ExamParticipationTest(TestCase):
    baker_recipe = "exam.exam_participation"

    @classmethod
    def setUpTestData(cls):
        """Set up the test data."""
        cls.user = baker.make(User, username="testuser")
        cls.exam = baker.make_recipe("exam.exam", title="Test Exam")
        cls.exam_participation = baker.make_recipe(
            cls.baker_recipe, user=cls.user, exam=cls.exam
        )

    def test_str(self):
        """Test the string representation of a question.
        Exam result's string representation should contain the user's
        username and the exam's title.
        """
        result_str = str(self.exam_participation)
        self.assertIn(self.user.username, result_str)
        self.assertIn(self.exam.title, result_str)

    def test_set_deadline_no_duration(self):
        """Test that the deadline is set to None if exam has no deadline
        duration.
        """
        exam: Exam = baker.make_recipe(
            ExamTest.bakery_recipe, deadline_duration=None
        )
        exam_participation: ExamParticipation = baker.make_recipe(
            "exam.exam_participation", exam=exam
        )

        self.assertIsNone(exam_participation.deadline)

    def test_set_deadline_with_duration(self):
        """Test that the deadline is set correctly when exam has a deadline."""
        exam: Exam = baker.make_recipe(
            ExamTest.bakery_recipe, deadline_duration=timedelta(hours=1)
        )
        exam_participation: ExamParticipation = baker.make_recipe(
            "exam.exam_participation", exam=exam
        )

        self.assertEqual(
            exam_participation.deadline,
            exam_participation.started_at + exam.deadline_duration,
        )


class ParticipantAnswerTest(TestCase):
    """Test the ParticipantAnswer model."""

    bakery_recipe = "exam.participant_answer"

    def test_model_uses_proper_queryset(self):
        """Test that the model uses the ParticipantAnswerQuerySet as
        its queryset manager."""
        self.assertIsInstance(
            ParticipantAnswer.objects.all(), ParticipantAnswerQuerySet
        )


class ExamLikeTest(TestCase):
    """Test the ExamLike model."""

    @classmethod
    def setUpTestData(cls):
        cls.designer_user = baker.make(User)
        cls.participant_user = baker.make(User)
        cls.nonparticipant_user = baker.make(User)
        cls.exam = baker.make_recipe("exam.exam", designer=cls.designer_user)

        baker.make_recipe(
            "exam.exam_participation", user=cls.participant_user, exam=cls.exam
        )

    def make_like(self):
        return baker.make_recipe(
            "exam.exam_like", user=self.participant_user, exam=self.exam
        )

    def test_nonparticipant_user(self):
        """Test that raises ValidationError when user is not a participant."""
        with self.assertRaises(ValidationError):
            baker.make_recipe(
                "exam.exam_like", user=self.nonparticipant_user, exam=self.exam
            )

    def test_participant_user(self):
        """Test that saves object when user is a participant."""
        like = self.make_like()
        self.assertIn(like, self.participant_user.exam_likes.all())

    def test_creation_score_coin(self):
        """Test that sets the score and coin correctly when user
        likes an exam.
        """
        old_score = self.participant_user.scores
        old_coin = self.participant_user.coins

        self.make_like()
        self.designer_user.refresh_from_db()

        self.assertEqual(
            self.designer_user.scores - old_score, config.EXAM_LIKE_SCORE
        )
        self.assertEqual(
            self.designer_user.coins - old_coin, config.EXAM_LIKE_COIN
        )

    def test_increase_likes_count(self):
        """Test that increases likes count on create."""
        like = self.make_like()
        self.assertEqual(like.exam.likes_count, 1)

    def test_decrease_likes_count(self):
        """Test that decreases likes count on delete."""
        self.make_like()
        like2 = self.make_like()
        like2.delete()

        like2.exam.refresh_from_db()

        self.assertEqual(like2.exam.likes_count, 1)
