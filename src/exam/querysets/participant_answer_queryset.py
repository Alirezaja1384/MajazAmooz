from django.db.models import QuerySet, When, Case, Q, F
from shared.models import AnswerStatusChoices


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

    def set_answers_status(self) -> int:
        """Sets the status of answers by matching the correct answers with the
        participant's answers.

        Returns:
            int: The number of answers that were set.
        """
        return self.update(
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
            )
        )
