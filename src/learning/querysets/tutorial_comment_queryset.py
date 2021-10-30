""" QuerySet for tutorial comment model """
from django.db.models import QuerySet
from . import get_active_confirmed_filters


class TutorialCommentQueryset(QuerySet):
    """TutorialComment queryset"""

    def active_and_confirmed_comments(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Confirmed tutorial comments
        """
        return self.filter(get_active_confirmed_filters())

    def active_confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Tutorial comments with active and confirmed tutorials
        """
        return self.filter(get_active_confirmed_filters("tutorial"))
