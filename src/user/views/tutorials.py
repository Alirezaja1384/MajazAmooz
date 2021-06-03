from django.forms import ModelForm
from django.contrib import messages
from django.views.generic import (CreateView, UpdateView)
from django.shortcuts import (reverse, redirect)
from django_tables2 import SingleTableView

from user.tables import TutorialTable
from user.forms import TutorialForm
from learning.models import Tutorial
from utilities.views.generic import (
    DynamicModelFieldDetailView, DeleteDeactivationView
)


SUCCESS_VIEW_NAME = 'user:tutorials'


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


class TutorialCreateView(CreateView):
    template_name = "user/tutorials/create_update.html"

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
    template_name = "user/tutorials/create_update.html"

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
    template_name = "user/tutorials/delete.html"
    context_object_name = 'tutorial'

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)
