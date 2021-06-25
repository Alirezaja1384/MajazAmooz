from django.db.models import QuerySet

from utilities.models import ConfirmStatusChoices


class TutorialUserRelationQuerySet(QuerySet):
    def active_confirmed_tutorials(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: objects with active and confirmed tutorial
        """
        return self.filter(tutorial__is_active=True,
                           tutorial__confirm_status=ConfirmStatusChoices.CONFIRMED)
