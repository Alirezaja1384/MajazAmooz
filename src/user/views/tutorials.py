from django.forms import ModelForm
from django.contrib import messages
from django.views.generic import (CreateView, UpdateView)
from django.shortcuts import (reverse, redirect)
from django_tables2 import SingleTableView

from user.tables import (TutorialTable, TutorialUserRelationsTable)
from user.forms import TutorialForm
from learning.models import (
    Tutorial, TutorialView,
    TutorialLike
)
from utilities.views.generic import (
    DynamicModelFieldDetailView, DeleteDeactivationView
)


PAGINATE_BY = 10
SUCCESS_VIEW_NAME = 'user:tutorials'


def get_tutorials_queryset(user):
    return Tutorial.objects.filter(author=user)


class TutorialListView(SingleTableView):
    table_class = TutorialTable

    paginate_by = PAGINATE_BY
    template_name = 'user/shared/list.html'

    def get_queryset(self):
        return get_tutorials_queryset(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'user:tutorial_create'
        return context


class TutorialDetailView(DynamicModelFieldDetailView):
    template_name = 'user/shared/details.html'

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)


class TutorialCreateView(CreateView):
    template_name = "user/shared/create_update.html"

    form_class = TutorialForm

    def form_valid(self, form: ModelForm):
        tutorial: Tutorial = form.save(commit=False)
        tutorial.author = self.request.user
        tutorial.save()

        messages.success(
            self.request, f'آموزش "{tutorial.title}" با موفقیت افزوده شد')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class TutorialUpdateView(UpdateView):
    template_name = "user/shared/create_update.html"

    form_class = TutorialForm

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)

    def form_valid(self, form: ModelForm):
        tutorial: Tutorial = form.save()

        messages.success(
            self.request, f'آموزش "{tutorial.title}" با موفقیت ویرایش شد')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class TutorialDeleteDeactivateView(DeleteDeactivationView):
    template_name = 'user/tutorials/delete.html'
    context_object_name = 'tutorial'

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class TutorialRelationsAbstractTableView(SingleTableView):
    table_class = TutorialUserRelationsTable

    paginate_by = PAGINATE_BY
    default_ordering = ('-create_date',)
    template_name = 'user/shared/list.html'

    def get_queryset(self):
        raise NotImplementedError('You should implement get_queryset()')


class TutorialsViewedByOthersListView(TutorialRelationsAbstractTableView):
    def get_queryset(self):
        return TutorialView.objects.filter(tutorial__author=self.request.user).order_by(
            *self.default_ordering).select_related('user', 'tutorial').active_confirmed_tutorials()


class TutorialsLikedByOthersListView(TutorialRelationsAbstractTableView):
    def get_queryset(self):
        return TutorialLike.objects.filter(tutorial__author=self.request.user).order_by(
            *self.default_ordering).select_related('user', 'tutorial').active_confirmed_tutorials()


class TutorialsLikedByMeListView(TutorialRelationsAbstractTableView):
    def get_queryset(self):
        return TutorialLike.objects.filter(user=self.request.user).order_by(
            *self.default_ordering).select_related('user', 'tutorial').active_confirmed_tutorials()
