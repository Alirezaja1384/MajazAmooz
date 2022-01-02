from django.db import models
from exam.querysets import ParticipantAnswerQuerySet
from shared.models import QUESTION_ANSWER_CHOICES, AnswerStatusChoices


class ParticipantAnswer(models.Model):
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

    class Meta:
        verbose_name = "پاسخ کاربر"
        verbose_name_plural = "پاسخ‌های کاربران"

    objects: ParticipantAnswerQuerySet = ParticipantAnswerQuerySet.as_manager()
