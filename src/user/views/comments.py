from django_tables2 import SingleTableView
from learning.models import TutorialComment
from authentication.models import User
from user.tables import TutorialCommentTable
from utilities.views.generic import DynamicModelFieldDetailView


# TODO: Make pagination dynamic
PAGINATE_BY = 10


def get_tutorial_comments_queryset(user: User):
    return TutorialComment.objects.filter(user=user).select_related(
        'tutorial', 'parent_comment').active_confirmed_tutorials()


class TutorialCommentListView(SingleTableView):
    table_class = TutorialCommentTable

    paginate_by = PAGINATE_BY
    template_name = 'user/shared/list.html'

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)


class TutorialCommentDetailsView(DynamicModelFieldDetailView):

    paginate_by = PAGINATE_BY
    template_name = 'user/shared/details.html'

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)
