from datetime import timedelta
from unittest.mock import patch
from constance import config
from model_bakery import baker
from django.test import TestCase
from django.utils import timezone
from django.db.utils import DatabaseError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from authentication.models import User
from exam.models.exam_like import ExamLike
from exam.querysets import ParticipantAnswerQuerySet
from exam.models import (
    Exam,
    Question,
    ExamParticipation,
    ParticipantAnswer,
)


UserModel = get_user_model()


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

    def test_clean_blank_score_greater_than_correct_score(self):
        """Test that the clean method raises a ValidationError when the blank score
        is greater than the correct score.
        """
        exam: Exam = baker.make_recipe(
            self.bakery_recipe,
            correct_score=2,
            blank_score=5,
            incorrect_score=-1,
        )
        self.assertRaises(ValidationError, exam.full_clean)

    def test_clean_incorrect_score_greater_than_blank_score(self):
        """Test that the clean method raises a ValidationError when the incorrect score
        is greater than the blank score.
        """
        exam: Exam = baker.make_recipe(
            self.bakery_recipe,
            correct_score=2,
            blank_score=0,
            incorrect_score=1,
        )
        self.assertRaises(ValidationError, exam.full_clean)

    def test_clean_ends_at_less_than_starts_at(self):
        """Test that the clean method raises a ValidationError when the ends_at
        is less than or equal to the starts_at.
        """
        # Ended before start
        exam: Exam = baker.make_recipe(
            self.bakery_recipe,
            ends_at=timezone.now() - timedelta(days=1),
            starts_at=timezone.now(),
        )
        self.assertRaises(ValidationError, exam.full_clean)


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
        cls.user: User = baker.make(UserModel, username="testuser")
        cls.exam: Exam = baker.make_recipe("exam.exam", title="Test Exam")
        cls.exam_participation: ExamParticipation = baker.make_recipe(
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
            ExamTest.bakery_recipe, deadline_duration=None, ends_at=None
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

        self.assertAlmostEqual(
            exam_participation.deadline,
            exam_participation.started_at + exam.deadline_duration,
            delta=timedelta(seconds=1),  # Max difference should be 1 second
        )

    def test_call_set_deadline_on_create(self):
        """Test that the _set_deadline method is called when creating an exam
        participation.
        """
        exam_participation: ExamParticipation = baker.prepare_recipe(
            self.baker_recipe, exam=self.exam, user=self.user
        )

        with patch.object(
            exam_participation, "_set_deadline"
        ) as mock_set_deadline:
            exam_participation.save()
            mock_set_deadline.assert_called_once()

    def test_not_call_set_deadline_on_update(self):
        """Test that the _set_deadline method is not called when updating an exam
        participation.
        """
        exam_participation: ExamParticipation = baker.make_recipe(
            self.baker_recipe, exam=self.exam, user=self.user
        )

        with patch.object(
            exam_participation, "_set_deadline"
        ) as mock_set_deadline:
            exam_participation.save()
            mock_set_deadline.assert_not_called()

    def test_set_deadline_deadline_duration_less_than_ends_at(self):
        """Test that sets the deadline by exam's deadline duration if the
        duration is less than the exam's ends_at.
        """
        self.exam.ends_at = timezone.now() + timedelta(days=1)
        self.exam.deadline_duration = timedelta(days=1)
        self.exam.save()

        exam_participation: ExamParticipation = baker.make_recipe(
            self.baker_recipe, exam=self.exam, user=self.user
        )
        self.assertAlmostEqual(
            exam_participation.deadline,
            timezone.now() + self.exam.deadline_duration,
            delta=timedelta(seconds=1),  # Max difference should be 1 second
        )

    def test_set_deadline_deadline_duration_greater_than_ends_at(self):
        """Test that sets the deadline by exam's ends_at if the deadline duration
        is greater than the exam's ends_at.
        """
        # Exam ends 10 minutes from now
        self.exam.ends_at = timezone.now() + timedelta(minutes=10)
        # But the deadline duration is an hour
        self.exam.deadline_duration = timedelta(hours=1)
        self.exam.save()

        exam_participation: ExamParticipation = baker.make_recipe(
            self.baker_recipe, exam=self.exam, user=self.user
        )

        self.assertEqual(
            exam_participation.deadline,
            self.exam.ends_at,
        )

    def test_finalize_exam_set_is_finalized_and_finalized_at(self):
        """Test that the is_finalized and finalized_at fields are set when
        finalizing an exam participation.
        """
        self.exam_participation.finalize_exam(commit=False)

        self.assertTrue(self.exam_participation.is_finalized)
        self.assertAlmostEqual(
            self.exam_participation.finalized_at,
            timezone.now(),
            delta=timedelta(seconds=1),  # Max difference should be 1 second
        )

    def test_finalize_exam_expired_deadline_raise_error(self):
        """Test that finalize_exam raises an error when the exam's deadline is
        expired.
        """
        # Exam participation's deadline has expired yesterday
        self.exam_participation.deadline = timezone.now() - timedelta(days=1)
        self.exam_participation.save()

        self.assertRaises(
            ValidationError,
            self.exam_participation.finalize_exam,
        )

    def test_finalize_exam_add_waiting_time_to_deadline(self):
        """Test that the waiting time is added to the deadline when finalizing
        an exam participation.
        """
        # exam_participation's deadline has expired 2 minutes ago
        self.exam_participation.deadline = timezone.now() - timedelta(
            minutes=2
        )
        self.exam_participation.save()

        # But the exam has a waiting time of 5 minutes
        self.exam.waiting_duration = timedelta(minutes=5)
        self.exam.save()

        # finalize_exam should not raise ValidationError
        try:
            self.exam_participation.finalize_exam(commit=False)
        except ValidationError:
            self.fail("finalize_exam did not add waiting time to the deadline")

    def test_finalize_exam_save_on_commit(self):
        """Test that finalize_exam saves the exam participation if commit is
        True.
        """
        with patch.object(self.exam_participation, "save") as mock_save:
            self.exam_participation.finalize_exam(commit=True)
            mock_save.assert_called_once()


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
        cls.designer_user: User = baker.make(UserModel)
        cls.participant_user: User = baker.make(UserModel)
        cls.nonparticipant_user: User = baker.make(UserModel)
        cls.exam: Exam = baker.make_recipe(
            "exam.exam", designer=cls.designer_user
        )

        baker.make_recipe(
            "exam.exam_participation", user=cls.participant_user, exam=cls.exam
        )

    def make_like(self, user=None):
        return baker.make_recipe(
            "exam.exam_like",
            exam=self.exam,
            user=user or self.participant_user,
        )

    def test_participant_user(self):
        """Test that saves object when user is a participant."""
        like = self.make_like()
        self.assertTrue(like.user.exam_likes.contains(like))

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
        like = self.make_like()
        like.delete()

        like.exam.refresh_from_db()
        self.assertEqual(like.exam.likes_count, 0)

    def test_unique_together(self):
        """Test that raises DatabaseError/ValidationError when user likes
        an exam more than once.
        """
        self.make_like()
        with self.assertRaises((DatabaseError, ValidationError)):
            self.make_like()

    def test_clean_designer_like(self):
        """Test that raises ValidationError when user likes an exam
        that designed by himself/herself.
        """
        # Participate designer user in exam to make sure the error is raised
        #  because user liked an exam that designed by himself/herself.
        baker.make_recipe(
            "exam.exam_participation", user=self.designer_user, exam=self.exam
        )

        like: ExamLike = self.make_like(user=self.designer_user)
        self.assertRaises(ValidationError, like.full_clean)

    def test_clean_nonparticipant_like(self):
        """Test that raises ValidationError when user is not a participant."""
        like: ExamLike = self.make_like(user=self.nonparticipant_user)
        self.assertRaises(ValidationError, like.full_clean)
