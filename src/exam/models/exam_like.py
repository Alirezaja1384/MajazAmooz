from constance import config
from django.db import models
from django.core.exceptions import ValidationError
from shared.models import AbstractScoreCoinModel


class ExamLike(AbstractScoreCoinModel):
    """ExamLike model"""

    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="exam_likes",
    )

    exam = models.ForeignKey(
        "exam.Exam",
        on_delete=models.CASCADE,
        related_name="likes",
    )

    # AbstractScoreCoinModel settings
    user_relation_field = "exam.designer"
    object_relation_field = "exam"
    object_relation_count_field_name = "likes_count"

    class Meta:
        verbose_name = "لایک آزمون"
        verbose_name_plural = "لایک آزمون ها"
        # Each user can't like the same exam more than once
        unique_together = ("user", "exam")

    def get_create_coin(self):
        return config.EXAM_LIKE_COIN

    def get_create_score(self):
        return config.EXAM_LIKE_SCORE

    def clean(self):
        """Checks if user has participated in the exam

        Raises:
            ValidationError: If user has not participated in the exam.
        """
        if not self.exam.results.filter(user=self.user).exists():
            # If user has not participated in the exam raise ValidationError
            raise ValidationError("شما در آزمون شرکت نکرده اید.")

        if self.exam.designer == self.user:
            # If user is the exam designer raise ValidationError
            raise ValidationError("شما نمیتوانید آزمون خودتان را لایک کنید.")
