""" QuerySet for tutorial model """
from django.db.models import QuerySet


class TutorialQuerySet(QuerySet):
    """ Tutorial queryset """

    def confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Confirmed tutorials
        """
        return self.filter(confirm_status=1)
