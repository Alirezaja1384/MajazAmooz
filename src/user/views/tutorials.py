from django.forms import ModelForm
from django.contrib import messages
from django.views.generic import (CreateView, UpdateView)
from django.shortcuts import (reverse, redirect)
from django_tables2 import SingleTableView
from constance import config
from user.tables import (TutorialTable, TutorialUserRelationsTable)
from user.forms import TutorialForm
from learning.models import (
    Tutorial, TutorialView,
    TutorialLike
)
from utilities.views.generic import (
    DynamicModelFieldDetailView, DeleteDeactivationView
)


SUCCESS_VIEW_NAME = 'user:tutorials'


def get_paginate_by():
    """ Note: defining paginate_by as a function is necessary to ensure it changes immediately.
    """
    return config.USER_PANEL_PAGINATE_BY


def get_tutorials_queryset(user):
    return Tutorial.objects.filter(author=user).select_related(
        'author').prefetch_related('tags', 'categories')


class TutorialListView(SingleTableView):
    table_class = TutorialTable
    template_name = 'user/shared/list.html'

    @property
    def paginate_by(self):
        """ Note: SingleTableView doesn't use get_paginate_by() currently, then
            defining paginate_by as a property is necessary to ensure it changes immediately.
        """
        return get_paginate_by()

    def get_queryset(self):
        return get_tutorials_queryset(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['create_url'] = 'user:tutorial_create'
        return context


class TutorialDetailView(DynamicModelFieldDetailView):

    def get_tags(self):
        return '، '.join([str(tag) for tag in self.object.tags.all()])
    get_tags.short_description = 'کلمات کلیدی'

    template_name = 'user/shared/details.html'
    additional_content = [get_tags]
    fields = ('title', 'slug', 'short_description', 'body', 'create_date',
              'last_edit_date', 'confirm_status', 'categories', get_tags, 'image',
              'user_views_count', 'up_votes_count', 'down_votes_count', 'likes_count',
              'is_edited', 'is_active',)

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)


class TutorialCreateView(CreateView):
    template_name = 'user/shared/create_update.html'

    form_class = TutorialForm

    def form_valid(self, form: ModelForm):
        tutorial: Tutorial = form.save(commit=False)
        # Set tutorial author
        tutorial.author = self.request.user
        # Save tutorial
        tutorial.save()
        # Save tutorial tags
        form.save_tags()

        messages.success(
            self.request, f'آموزش "{tutorial.title}" با موفقیت افزوده شد')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tagsinput_required'] = True
        return context


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
    template_name = 'user/shared/delete.html'
    context_object_name = 'tutorial'

    def get_queryset(self):
        return get_tutorials_queryset(self.request.user)

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class TutorialRelationsAbstractTableView(SingleTableView):
    table_class = TutorialUserRelationsTable

    default_ordering = ('-create_date',)
    template_name = 'user/shared/list.html'

    @property
    def paginate_by(self):
        """ Note: SingleTableView doesn't use get_paginate_by() currently, then
            defining paginate_by as a property is necessary to ensure it changes immediately.
        """
        return get_paginate_by()

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
