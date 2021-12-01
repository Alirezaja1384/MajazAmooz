from django.test import TestCase
from model_bakery import baker
from exam.models import Exam, Question


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
