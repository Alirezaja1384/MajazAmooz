from django.utils import timezone
from django.db.models import QuerySet
from shared.models import ExamParticipationStatusChoices
from exam.models import Exam
from exam.querysets.participant_answer_queryset import AnswerStatusCounts


class ExamParticipationQuerySet(QuerySet):
    """ExamParticipation queryset."""

    def get_finalized(self):
        """Get finalized exam results."""
        return self.filter(is_finalized=True)

    def get_in_progress(self):
        """Get in-progress (non-started) exam results."""
        return self.filter(is_finalized=False)

    def get_deadline_expired(self):
        """Get exam results that their deadlines have expired."""
        return self.filter(deadline__lt=timezone.now())

    def mark_participation_result(
        self, exam_participation, set_statuses=True, commit: bool = True
    ):
        """Marks the results of the exam.

        Args:
            exam_participation (ExamParticipation): The exam participation
                to mark and save (when commit is True).

            set_statuses (bool): Whether to set the status of the answers
                before marking the result.

            commit (bool): Whether to commit the changes to the database.

        Returns:
            ExamParticipation: The marked exam participation.
        """
        exam: Exam = exam_participation.exam
        questions_count: int = exam.questions.count()

        status_counts: AnswerStatusCounts = (
            exam_participation.answers.all().aggregate_answer_statuses_count(
                set_statuses=set_statuses
            )
        )

        # <-- Total answer status counts -->
        exam_participation.total_blank = status_counts.blank
        exam_participation.total_correct = status_counts.correct
        exam_participation.total_incorrect = status_counts.incorrect
        # </-- Total answer status counts -->

        # <-- Coin calculation -->
        exam_participation.coin_earned = (
            status_counts.correct * exam.correct_coin
        )
        # </-- Coin calculation -->

        # <-- Score calculations -->
        exam_participation.score_max = questions_count * exam.correct_score
        # Sum of scores of all answered questions
        exam_participation.score_earned = (
            exam_participation.total_blank * exam.blank_score
            + exam_participation.total_correct * exam.correct_score
            + exam_participation.total_incorrect * exam.incorrect_score
        )
        # Calculate score percent and round it to 2 decimal places.
        exam_participation.score_percent = round(
            (exam_participation.score_earned / exam_participation.score_max)
            * 100,
            2,
        )
        # </-- Score calculations -->

        # <-- Set statuses -->
        exam_participation.is_finalized = True
        exam_participation.mark_status = (
            ExamParticipationStatusChoices.COMPLETED
        )
        # </-- Set statuses -->

        if commit:
            exam_participation.save()

        return exam_participation
