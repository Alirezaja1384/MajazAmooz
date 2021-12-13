from constance import config
from django.db import models
from django.forms import ValidationError
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

    def get_create_coin(self):
        return config.EXAM_LIKE_COIN

    def get_create_score(self):
        return config.EXAM_LIKE_SCORE

    def clean_fields(self, exclude=None):
        """Checks if user has participated in the exam

        Raises:
            ValidationError: If user has not participated in the exam.
        """
        super().clean_fields(exclude=exclude)
        if not self.exam.results.filter(user=self.user).exists():
            # If user has not participated in the exam raise ValidationError
            raise ValidationError({"user": "شما در آزمون شرکت نکرده اید."})

    def save(self, *args, **kwargs):
        # Validate user participation
        self.full_clean()
        # Save the model
        super().save(*args, **kwargs)
