"""TypedDict classes used in this project"""
from math import ceil
from typing import TypedDict
from authentication.models import User


class MonthlyCountStatistics(TypedDict):
    """Count of items per jalali-month"""

    label: str
    count: int


class TutorialStatistics(TypedDict):
    """Tutorial statistics"""

    tutorials_count: int
    likes_count: int
    views_count: int
    comments_count: int


class UserPanelStatistics:
    def __init__(
        self,
        user: User,
        tutorials_statistics: TutorialStatistics,
        view_statistics: list[MonthlyCountStatistics],
    ):
        self.user = user
        self.tutorials_statistics = tutorials_statistics
        self.view_statistics = view_statistics

        # Calculate goal completion percents dynamically
        self.calculate_goal_completion_percents()

    def calculate_goal_completion_percents(self):
        """Automatically generates goal completion percents.

        Looks for tutorials_statistics keys and get their goals,
        then calculates their completion percents.

        Example:
            Input:
                self.tutorials_statistics["tutorials_count"] = 100
                self.user_goals["tutorials_count_goal"] = 150
            Output:
                self.tutorials_count_goal_percent = 60
        """

        def _calculate_goal_completion_percent(
            value: int, goal_value: int
        ) -> int:
            """Calculates completion percent of each goal.

            Args:
                value (int): Current value.
                goal_value (int): Goal value.

            Special cases:
                value > goal_value: returns 100.
                goal_value == 0: returns 100.

            Returns:
                int: Completion percent of each goal.
            """
            if goal_value == 0 or value > goal_value:
                return 100
            return ceil((value / goal_value) * 100)

        # Look for statistics values
        for key in self.tutorials_statistics.keys():
            # Set goal percent
            setattr(
                self,
                key + "_goal_percent",
                _calculate_goal_completion_percent(
                    # Get currect value.
                    self.tutorials_statistics[key],
                    # Get goal value. Defaults to 0.
                    getattr(self.user, key + "_goal", 0),
                ),
            )
