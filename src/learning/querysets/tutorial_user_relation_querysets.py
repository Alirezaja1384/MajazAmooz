from datetime import date
from typing import Optional
from django.db.models import QuerySet, When, Case, Sum
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

    def get_last_months_count_statistics(
        self,
        last_months_count: int = 5,
        today: Optional[date] = None,
        ascending: bool = True,
    ) -> list[MonthlyCountStatistics]:
        """Calculates count of objects per last given jalali months.

        Args:
            last_months_count (int, optional): Count of last months to
                calculate. Defaults to 5.

        Yields:
            list[MonthlyCountStatistics]: Month's label and
                count of object for that month.
        """
        # Make a When condition for each month
        conditions = {
            # Calculates sum of 1s for each item created in this month
            month.label: Sum(
                Case(
                    # If item is created in this month it's 1
                    When(
                        create_date__gte=month.gregorian_start,
                        create_date__lte=month.gregorian_end,
                        then=1,
                    ),
                    # Otherwise, it's 0
                    default=0,
                )
            )
            for month in get_last_months(last_months_count, today)
        }

        count_statistics: list[MonthlyCountStatistics] = [
            # Convert aggregated count to MonthlyCountStatistics
            MonthlyCountStatistics(
                {"label": agg_result[0], "count": agg_result[1]}
            )
            for agg_result in self.aggregate(**conditions).items()
        ]

        # If ascending is True, reverse it and return (Because months are
        # sorted in descending order, thus statistics' sort is descending too).
        # Otherwise, return count_statistics itself.
        return count_statistics[::-1] if ascending else count_statistics
