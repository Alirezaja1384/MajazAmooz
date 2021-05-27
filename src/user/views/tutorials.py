from django_tables2 import SingleTableView
from learning.models import Tutorial
from user.tables import TutorialTable
from utilities.views.generic import DynamicModelFieldDetailView


def get_tutorials_queryset(user):
    return Tutorial.objects.filter(author=user)


class TutorialListView(SingleTableView):
    table_class = TutorialTable

    paginate_by = 10
    template_name = 'user/tutorials/index.html'

    def get_queryset(self):
        return get_tutorials_queryset(user=self.request.user)


class TutorialDetailView(DynamicModelFieldDetailView):
    template_name = 'user/tutorials/details.html'

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)
