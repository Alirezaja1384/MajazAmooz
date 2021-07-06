from typing import Generator
from django.db.models import QuerySet
from shared.models import ConfirmStatusChoices
from shared.date_time import get_last_months
from shared.statistics import MonthlyCountStatistics


class TutorialUserRelationQueryset(QuerySet):
    def active_confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: objects with active and confirmed tutorial
        """
        return self.filter(
            tutorial__is_active=True,
            tutorial__confirm_status=ConfirmStatusChoices.CONFIRMED,
        )

    # TODO: Improve performance by reducing query count
    def get_last_months_count_statistics(
        self, last_months_count=5
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
        last_months = list(get_last_months(last_months_count))[::-1]

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
