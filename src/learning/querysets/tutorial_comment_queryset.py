""" QuerySet for tutorial comment model """
from django.db.models import QuerySet


class TutorialCommentQueryset(QuerySet):
    """ TutorialComment queryset """

    def active_and_confirmed_comments(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: Confirmed tutorials comments
        """
        return self.filter(is_active=True, confirm_status=1)
