from datetime import date
from typing import Generator, Optional
from django.db.models import QuerySet
from shared.date_time import get_last_months
from shared.statistics import MonthlyCountStatistics
from . import get_active_confirmed_filters


class TutorialUserRelationQueryset(QuerySet):
    def active_confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: objects with active and confirmed tutorial
        """
        return self.filter(get_active_confirmed_filters("tutorial"))

    # TODO: Improve performance by reducing query count
    def get_last_months_count_statistics(
        self, last_months_count: int = 5, today: Optional[date] = None
    ) -> Generator[MonthlyCountStatistics, None, None]:
        """Calculates count of objects per last given jalali months.

        Args:
            last_months_count (int, optional): Count of last months to
                calculate. Defaults to 5.

        Yields:
            Generator[MonthlyCountStatistics, None, None]: Month's label and
                count of object for that month.
        """
        # Convert descending months data to ascending
        last_months = list(get_last_months(last_months_count, today))[::-1]

        for month in last_months:
            yield MonthlyCountStatistics(
                {
                    "label": month.label,
                    "count": self.filter(
                        create_date__gte=month.gregorian_start,
                        create_date__lte=month.gregorian_end,
                    ).count(),
                }
            )
