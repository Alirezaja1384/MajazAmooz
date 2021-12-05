from django.db.models import IntegerChoices


class ConfirmStatusChoices(IntegerChoices):
    """
    Confirm status choices:
        1 : Confirmed
        0 : Waiting for confirm
        -1 : disproved
    """

    WAITING_FOR_CONFIRM = 0, "در انتظار تایید"
    CONFIRMED = 1, "تایید شده"
    DISPROVED = -1, "رد شده"


class ExamResultStatusChoices(IntegerChoices):
    """
    Exam result status choices:
        3 : Finalized and Marked
        2 : Finalized and waiting for mark
        1 : Still in progress
    """

    IN_PROGRESS = 1, "در حال تکمیل"
    WAITING_FOR_MARK = 2, "در انتظار صدور کارنامه"
    MARKED = 3, "کارنامه صادر شده"


QUESTION_ANSWER_CHOICES = [(i, f"گزینه {i}") for i in range(1, 5)]


class AnswerStatusChoices(IntegerChoices):
    """
    Answer status choices:
        1 : Correct
        0 : Blank
        -1 : Incorrect
    """

    CORRECT = 1, "صحیح"
    INCORRECT = -1, "غلط"
    BLANK = 0, "نزده"
