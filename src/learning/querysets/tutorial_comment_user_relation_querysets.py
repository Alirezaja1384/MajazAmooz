from django.db.models import QuerySet
from . import get_active_confirmed_filters


class TutorialCommentUserRelationQueryset(QuerySet):
    def active_confirmed_comments(self) -> QuerySet:
        """
        Returns:
            [QuerySet]: objects with active and confirmed comment
        """
        return self.filter(get_active_confirmed_filters("comment"))
