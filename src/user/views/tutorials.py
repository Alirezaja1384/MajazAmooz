from django_tables2 import SingleTableView

from learning.models import Tutorial
from user.tables import TutorialTable


class TutorialListView(SingleTableView):
    table_class = TutorialTable
    paginate_by = 10
    template_name = 'user/tutorials/index.html'

    def get_queryset(self):
        return Tutorial.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'مدیریت آموزش ها'
        return context
