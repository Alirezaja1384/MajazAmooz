from django.db import models
from django_lifecycle import LifecycleModel
from shared.models import QUESTION_ANSWER_CHOICES


class Question(LifecycleModel):
    """Question model"""

    ANSWER_HELP_TEXT = (
        "پاسخ پس از اتمام زمان آزمون برای دانش آموز نمایش داده می شود"
    )

    question_text = models.TextField(max_length=500, verbose_name="متن سوال")

    # Choices
    choice_1 = models.CharField(max_length=100, verbose_name="گزینه اول")
    choice_2 = models.CharField(max_length=100, verbose_name="گزینه دوم")
    choice_3 = models.CharField(max_length=100, verbose_name="گزینه سوم")
    choice_4 = models.CharField(max_length=100, verbose_name="گزینه چهارم")

    # Answers
    correct_choice = models.IntegerField(
        choices=QUESTION_ANSWER_CHOICES,
        verbose_name="جواب صحیح",
        help_text=ANSWER_HELP_TEXT,
    )
    correct_full_answer = models.TextField(
        max_length=1000,
        verbose_name="پاسخ تشریحی",
        help_text=ANSWER_HELP_TEXT,
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # Relations
    exam = models.ForeignKey("exam.Exam", null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوالات"
