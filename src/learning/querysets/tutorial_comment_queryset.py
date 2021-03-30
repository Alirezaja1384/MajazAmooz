""" QuerySet for tutorial comment model """
from django.db.models import QuerySet


class TutorialCommentQueryset(QuerySet):
    """ TutorialComment queryset """

    def confirmed_comments(self):
        """
        Returns:
            [QuerySet]: Confirmed tutorial comments
        """
        return self.filter(confirm_status=1)
