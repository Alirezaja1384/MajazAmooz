from typing import Optional
from datetime import datetime, date
from django.utils import timezone
import jdatetime


class JalaliMonth:
    def __init__(
        self,
        gregorian_start: datetime,
        gregorian_end: datetime,
        label: Optional[str] = None,
    ):
        self.gregorian_start = timezone.make_aware(gregorian_start)
        self.gregorian_end = timezone.make_aware(gregorian_end)
        self.label = label

    def __eq__(self, other):
        return (
            self.gregorian_start == other.gregorian_start
            and self.gregorian_end == other.gregorian_end
        )

    def __repr__(self):
        return f"{self.gregorian_start} - {self.gregorian_end}"


def normalize_month(month: int):
    # Month can't be 0 or negative. thus,
    # decreases 1 month then calculate its remainder
    # (to ensure the value is not negative)
    # and increases 1 at end
    return (month - 1) % 12 + 1


def get_last_months(count: int = 1, today: Optional[date] = None):

    if not today:
        today = date.today()

    jdatetime.set_locale("fa_IR")
    today_jalali = jdatetime.date.fromgregorian(date=today)

    # Year will decrease if month<0
    year = today_jalali.year
    # Month will decrease in every loop
    month = today_jalali.month + 1

    # for each last month
    for _ in range(count):

        # Decrease 1 month, If result is negative
        # decrease year and normalize month
        month -= 1
        if month <= 0:
            year -= 1
            month = normalize_month(month)

        start_date = jdatetime.datetime(year, month, 1)

        # end_date_month is 1 month after start. If result is more than 12,
        # set end_date_year to 1 year after start year and normalize month,
        # otherwise set  to start date year.
        end_date_month = month + 1
        if month >= 12:
            end_date_month = normalize_month(end_date_month)
            end_date_year = year + 1
        else:
            end_date_year = year

        end_date = jdatetime.datetime(end_date_year, end_date_month, 1)

        yield JalaliMonth(
            start_date.togregorian(),
            end_date.togregorian(),
            start_date.strftime("%b %Y"),
        )
