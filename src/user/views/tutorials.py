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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'مدیریت آموزش ها'
        return context


class TutorialDetailView(DynamicModelFieldDetailView):
    template_name = 'user/tutorials/details.html'

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'اطلاعات آموزش'
        return context
