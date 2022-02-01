from django.db.models import QuerySet, Subquery, OuterRef, When, Case, Q, F
from shared.models import AnswerStatusChoices
from exam.models import Question


class ParticipantAnswerQuerySet(QuerySet):
    """
    This class represents a participant's answer to a question.
    """

    def get_correct_answers(self):
        """
        Returns a queryset of all correct answers.
        """
        return self.filter(answer_status=AnswerStatusChoices.CORRECT)

    def get_incorrect_answers(self):
        """
        Returns a queryset of all incorrect answers.
        """
        return self.filter(answer_status=AnswerStatusChoices.INCORRECT)

    def get_blank_answers(self):
        """
        Returns a queryset of all blank answers.
        """
        return self.filter(answer_status=AnswerStatusChoices.BLANK)

    def set_correct_answers(self) -> int:
        """Sets the correct answers' choices by the question.

        Returns:
            int: Updated rows count.
        """
        return self.update(
            correct_answer=Subquery(
                # Sets the correct answer by the question.
                queryset=Question.objects.filter(
                    pk=OuterRef("question_id")
                ).values("correct_choice")[:1],
            ),
        )

    def set_answers_status(self) -> int:
        """Updates the correct answers (form their question) and answers' status
        by matching the correct answers with the participant's answers.

        Returns:
            int: The number of answers that were set.
        """
        # set the correct answer by the question.
        self.set_correct_answers()

        update_count = self.update(
            answer_status=Case(
                # If user's answer is null, then set the answer status
                # to blank.
                When(
                    Q(participant_answer__isnull=True),
                    then=AnswerStatusChoices.BLANK,
                ),
                # If user's answer is same as correct answer, then set the
                # answer status to correct.
                When(
                    Q(participant_answer=F("correct_answer")),
                    then=AnswerStatusChoices.CORRECT,
                ),
                # Otherwise, set the answer status to incorrect.
                default=AnswerStatusChoices.INCORRECT,
            ),
        )

        return update_count
