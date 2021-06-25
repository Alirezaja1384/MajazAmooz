""" QuerySet for tutorial comment model """
from django.db.models import QuerySet

from shared.models import ConfirmStatusChoices


class CategoryQueryset(QuerySet):
    """ Category queryset """

    def active_categories(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Active categories
        """
        return self.filter(is_active=True)
