from datetime import date
import jdatetime
from jdatetime.jalali import j_days_in_month


class PersiamMonth:

    def __init__(self, gregorian_start: date, gregorian_end: date, label: str):
        self.gregorian_start = gregorian_start
        self.gregorian_end = gregorian_end
        self.label = label

    def __repr__(self):
        return self.label


def get_month(month: int):
    # Month can't be 0 or negative then
    # we decrease 1 month then calculate its remainder
    # (to ensure the value is not negative)
    # then increase 1 at end
    return (month - 1) % 12 + 1


def get_last_months(count: int = 1):

    jdatetime.set_locale('fa_IR')
    today_jalali = jdatetime.date.today()

    # for each past month
    for i in range(count):

        # Calculate how many years left in {i} month ago
        left_years = ((i - today_jalali.month) // 12) + 1

        j_year_month = {
            'year': today_jalali.year - left_years,
            'month': get_month(today_jalali.month - i)
        }

        # month 1st
        start_date = jdatetime.date(j_year_month['year'],
                                    j_year_month['month'], 1,
                                    locale='fa_IR')

        # Last day of month
        end_date = jdatetime.date(
            j_year_month['year'],
            j_year_month['month'],
            j_days_in_month[j_year_month['month'] - 1],
            locale='fa_IR')

        yield PersiamMonth(start_date.togregorian(), end_date.togregorian(),
                           start_date.strftime('%b %Y'))
