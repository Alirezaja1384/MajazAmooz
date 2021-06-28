import datetime
from django.test import TestCase
from django.utils import timezone
from shared import date_time


class JalaliMonthTest(TestCase):
    def test_aware_times(self):
        """JalaliMonth should make datetimes aware automatically."""
        month = date_time.JalaliMonth(
            datetime.datetime(2021, 6, 22),
            datetime.datetime(2021, 7, 23),
        )

        self.assertTrue(timezone.is_aware(month.gregorian_start))
        self.assertTrue(timezone.is_aware(month.gregorian_end))


class NormalizeMonthTest(TestCase):
    def test_normalize_month(self):
        """get_month should return an integer between 1-12
        for any integer input. Forexample it should return 3 for 15.
        """

        # First: given value
        # Second: expected result
        test_cases = [
            (12, 12),
            (15, 3),
            (24, 12),
            (0, 12),
            (-5, 7),
            (-24, 12),
        ]

        for case in test_cases:
            self.assertEqual(date_time.normalize_month(case[0]), case[1])


class LastMonthsTest(TestCase):
    def test_get_last_months(self):
        """get_last_months should return last 'count' months
        from 'today' argument.
        """
        # Lables won't compare, Thus they're unnecessary
        test_cases = [
            # Common year (1400)
            {
                "count": 3,
                "today": datetime.date(2021, 7, 14),
                "expected_result": [
                    date_time.JalaliMonth(
                        datetime.datetime(2021, 6, 22),
                        datetime.datetime(2021, 7, 23),
                    ),
                    date_time.JalaliMonth(
                        datetime.datetime(2021, 5, 22),
                        datetime.datetime(2021, 6, 22),
                    ),
                    date_time.JalaliMonth(
                        datetime.datetime(2021, 4, 21),
                        datetime.datetime(2021, 5, 22),
                    ),
                ],
            },
            # Leap year (1399)
            {
                "count": 2,
                "today": datetime.date(2021, 4, 5),
                "expected_result": [
                    date_time.JalaliMonth(
                        datetime.datetime(2021, 3, 21),
                        datetime.datetime(2021, 4, 21),
                    ),
                    date_time.JalaliMonth(
                        datetime.datetime(2021, 2, 19),
                        datetime.datetime(2021, 3, 21),
                    ),
                ],
            },
        ]

        for case in test_cases:
            result = list(
                date_time.get_last_months(case["count"], case["today"])
            )

            self.assertEqual(result, case["expected_result"])

    def test_month_label(self):
        """get_last_months should return a JalaliMonth
        that has a label containing 'year + month name'.
        """
        months = list(date_time.get_last_months(4, datetime.date(2021, 6, 14)))
        expected_labels = [
            "خرداد 1400",
            "اردیبهشت 1400",
            "فروردین 1400",
            "اسفند 1399",
        ]

        for index, month in enumerate(months):
            self.assertEqual(month.label, expected_labels[index])
