""" QuerySet for tutorial comment model """
from django.db.models import QuerySet

from utilities.models import ConfirmStatusChoices


class TutorialCommentQueryset(QuerySet):
    """ TutorialComment queryset """

    def active_and_confirmed_comments(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Confirmed tutorial comments
        """
        return self.filter(is_active=True, confirm_status=ConfirmStatusChoices.CONFIRMED)

    def active_confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Tutorial comments with active and confirmed tutorials
        """
        return self.filter(tutorial__is_active=True,
                           tutorial__confirm_status=ConfirmStatusChoices.CONFIRMED)
