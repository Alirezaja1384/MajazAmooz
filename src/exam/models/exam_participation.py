from django.db import models
from django.utils import timezone
from django_lifecycle import LifecycleModel, hook, BEFORE_CREATE
from shared.models import ExamParticipationStatusChoices


class ExamParticipation(LifecycleModel):
    """A model that represents a user's participation in an exam."""

    started_at = models.DateTimeField(
        null=False, default=timezone.now, verbose_name="شروع شده در"
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
    score_percent = models.IntegerField(default=0, verbose_name="درصد امتیاز")

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
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="آزمون",
    )

    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="exam_participations",
        verbose_name="کاربر",
    )

    questions = models.ManyToManyField(
        through="exam.ParticipantAnswer",
        to="exam.Question",
        related_name="exam_participations",
    )

    @hook(BEFORE_CREATE)
    def before_create(self):
        """Set default values."""
        # Set the deadline if deadline_duration is set
        if self.exam.deadline_duration:
            self.deadline = self.started_at + self.exam.deadline_duration

    def __str__(self):
        """Return string representation."""
        return f"{self.exam.title} - {self.user.username}"

    class Meta:
        verbose_name = "نتیجه آزمون"
        verbose_name_plural = "نتیجه آزمون ها"
