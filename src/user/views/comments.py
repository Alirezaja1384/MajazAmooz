from django.forms import ModelForm
from django.contrib import messages
from django.shortcuts import (redirect, reverse)
from django.views.generic import UpdateView
from django_tables2 import SingleTableView
from learning.models import TutorialComment
from authentication.models import User
from user.tables import TutorialCommentTable
from user.forms import TutorialCommentForm
from utilities.views.generic import DynamicModelFieldDetailView


# TODO: Make pagination dynamic
PAGINATE_BY = 10
SUCCESS_VIEW_NAME = 'user:tutorial_comments'


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

    template_name = 'user/shared/details.html'

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)


class TutorialCommentUpdateView(UpdateView):
    form_class = TutorialCommentForm
    template_name = 'user/shared/create_update.html'

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)

    def form_valid(self, form: ModelForm):
        comment: TutorialComment = form.save(commit=False)
        comment.user = self.request.user
        comment.save()

        messages.success(
            self.request, f'دیدگاه "{comment.title}" با موفقیت ویرایش شد')

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)
