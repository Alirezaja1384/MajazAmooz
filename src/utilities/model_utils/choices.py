from django.db.models import IntegerChoices


class ConfirmStatusChoices(IntegerChoices):
    """
    Confirm status choices:
        1 : Confirmed
        0 : Waiting for confirm
        -1 : disproved
    """
    WAITING_FOR_CONFIRM = 0, 'در انتظار تایید'
    CONFIRMED = 1, 'تایید شده'
    DISPROVED = -1, 'رد شده'
