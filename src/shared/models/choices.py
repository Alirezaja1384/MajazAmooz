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

    NOT_STARTED = 1, "پردازش شروع نشده"
    IN_PROGRESS = 2, "در حال پردازش"
    COMPLETED = 3, "پردازش تمام شده"


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
