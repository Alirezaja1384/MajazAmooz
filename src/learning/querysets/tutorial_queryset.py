""" QuerySet for tutorial model """
from django.db.models import QuerySet


class TutorialQuerySet(QuerySet):
    """ Tutorial queryset """

    def active_and_confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Confirmed tutorials
        """
        return self.filter(is_active=True, confirm_status=1)
