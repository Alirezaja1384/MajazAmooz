from django.db import models
from django_lifecycle import LifecycleModel, hook, BEFORE_SAVE
from shared.models import QUESTION_ANSWER_CHOICES, AnswerStatusChoices


class ParticipantAnswer(LifecycleModel):
    """
    This model represents a participant's answer to a question.
    """

    participant_answer = models.IntegerField(
        choices=QUESTION_ANSWER_CHOICES, null=True
    )
    correct_answer = models.IntegerField(
        choices=QUESTION_ANSWER_CHOICES, null=False
    )
    answer_status = models.IntegerField(
        choices=AnswerStatusChoices.choices,
        default=AnswerStatusChoices.BLANK,
        null=False,
    )

    # Relations
    exam_result = models.ForeignKey(
        "exam.ExamResult",
        null=False,
        related_name="answers",
        on_delete=models.CASCADE,
    )

    question = models.ForeignKey(
        "exam.Question",
        null=False,
        related_name="answers",
        on_delete=models.CASCADE,
    )

    @hook(BEFORE_SAVE)
    def before_save(self, *args, **kwargs):
        """Before save actions"""
        # If answer is correct, set status to correct
        if self.participant_answer == self.correct_answer:
            self.answer_status = AnswerStatusChoices.CORRECT
        # If answer is incorrect, set status to incorrect
        elif self.participant_answer is not None:
            self.answer_status = AnswerStatusChoices.INCORRECT
        # If answer is blank, set status to blank
        else:
            self.answer_status = AnswerStatusChoices.BLANK

    class Meta:
        verbose_name = "پاسخ کاربر"
        verbose_name_plural = "پاسخ‌های کاربران"
