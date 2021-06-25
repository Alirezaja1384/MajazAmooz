from django.db.models import QuerySet

from shared.models import ConfirmStatusChoices


class TutorialCommentUserRelationQuerySet(QuerySet):
    def active_confirmed_comments(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: objects with active and confirmed comment
        """
        return self.filter(comment__is_active=True,
                           comment__confirm_status=ConfirmStatusChoices.CONFIRMED)
