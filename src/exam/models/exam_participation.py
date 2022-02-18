from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from shared.models import ExamParticipationStatusChoices
from exam.querysets import ExamParticipationQuerySet


class ExamParticipation(models.Model):
    """A model that represents a user's participation in an exam."""

    started_at = models.DateTimeField(
        null=False,
        editable=False,
        default=timezone.now,
        verbose_name="شروع شده در",
    )
    finalized_at = models.DateTimeField(
        null=True, verbose_name="پایان یافته در"
    )
    deadline = models.DateTimeField(null=True, verbose_name="مهلت پایان")

    total_correct = models.IntegerField(default=0, verbose_name="تعداد صحیح")
    total_incorrect = models.IntegerField(default=0, verbose_name="تعداد غلط")
    total_blank = models.IntegerField(default=0, verbose_name="تعداد نزده")

    coin_cost = models.IntegerField(default=0, verbose_name="هزینه سکه")
    coin_earned = models.IntegerField(default=0, verbose_name="سکه دریافتی")
    diamond_cost = models.IntegerField(default=0, verbose_name="هزینه الماس")

    score_earned = models.IntegerField(
        default=0, verbose_name="امتیاز کسب شده"
    )
    score_max = models.IntegerField(default=0, verbose_name="حداکثر امتیاز")
    score_percent = models.DecimalField(
        default=0,
        max_digits=5,  # Max value is 100.00
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="درصد امتیاز",
    )

    mark_status = models.IntegerField(
        choices=ExamParticipationStatusChoices.choices,
        default=ExamParticipationStatusChoices.NOT_STARTED,
        verbose_name="وضعیت کارنامه",
    )
    is_finalized = models.BooleanField(
        default=False, verbose_name="پایان یافته"
    )

    # Relations
    exam = models.ForeignKey(
        "exam.Exam",
        editable=False,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="آزمون",
    )

    user = models.ForeignKey(
        "authentication.User",
        editable=False,
        on_delete=models.CASCADE,
        related_name="exam_participations",
        verbose_name="کاربر",
    )

    questions = models.ManyToManyField(
        to="exam.Question",
        through="exam.ParticipantAnswer",
        related_name="exam_participations",
    )

    objects: ExamParticipationQuerySet = ExamParticipationQuerySet.as_manager()

    def _set_deadline(self):
        # Set the deadline if deadline_duration is set or exam has expiration
        if self.exam.deadline_duration or self.exam.ends_at:
            deadlines = []
            if self.exam.ends_at:
                deadlines.append(self.exam.ends_at)
            if self.exam.deadline_duration:
                deadlines.append(timezone.now() + self.exam.deadline_duration)

            # Use minimum deadline as the participation deadline
            self.deadline = min(deadlines)

    def finalize_exam(self, commit=True):
        """Finalizes the exam by setting the is_finalized and finalized_at
        fields.
        """
        self.is_finalized = True
        self.finalized_at = timezone.now()

        if (
            self.deadline
            and (self.deadline + (self.exam.waiting_duration or timedelta(0)))
            < timezone.now()
        ):
            raise ValidationError("مهلت آزمون به پایان رسیده است.")

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        """Sets the deadline and saves the model."""
        # Set deadline on first save
        if not self.pk:
            self._set_deadline()

        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation."""
        return f"{self.exam.title} - {self.user.username}"

    class Meta:
        verbose_name = "نتیجه آزمون"
        verbose_name_plural = "نتیجه آزمون ها"
