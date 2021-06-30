from django.forms import ModelForm
from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.views.generic import UpdateView
from django_tables2 import SingleTableView
from constance import config
from learning.models import TutorialComment, TutorialCommentLike
from learning.querysets import (
    TutorialQueryset,
    TutorialCommentUserRelationQueryset,
)
from authentication.models import User
from user.tables import (
    TutorialCommentTable,
    RepliedTutorialCommentTable,
    TutorialCommentUserRelationsTable,
)
from user.forms import TutorialCommentForm
from shared.views.generic import (
    DynamicModelFieldDetailView,
    DeleteDeactivationView,
)


SUCCESS_VIEW_NAME = "user:tutorial_comments"


def get_paginate_by():
    """Note: defining paginate_by as a function is necessary to ensure it changes immediately."""
    return config.USER_PANEL_PAGINATE_BY


def get_tutorial_comments_queryset(user: User) -> TutorialQueryset:
    return (
        TutorialComment.objects.filter(user=user)
        .select_related("tutorial", "parent_comment")
        .active_confirmed_tutorials()
    )


def get_tutorial_comment_like_queryset() -> TutorialCommentUserRelationQueryset:
    return TutorialCommentLike.objects.select_related(
        "user", "comment", "comment__tutorial", "comment__user"
    ).active_confirmed_comments()


class TutorialCommentListView(SingleTableView):
    table_class = TutorialCommentTable

    template_name = "user/shared/list.html"

    @property
    def paginate_by(self):
        """Note: SingleTableView doesn't use get_paginate_by() currently, then
        defining paginate_by as a property is necessary to ensure it changes immediately.
        """
        return get_paginate_by()

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)


class TutorialCommentDetailsView(DynamicModelFieldDetailView):

    template_name = "user/shared/details.html"

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)


class TutorialCommentUpdateView(UpdateView):
    form_class = TutorialCommentForm
    template_name = "user/shared/create_update.html"

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)

    def form_valid(self, form: ModelForm):
        comment: TutorialComment = form.save(commit=False)
        comment.user = self.request.user
        comment.save()

        messages.success(
            self.request, f'دیدگاه "{comment.title}" با موفقیت ویرایش شد'
        )

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class TutorialCommentDeleteDeactivateView(DeleteDeactivationView):
    template_name = "user/shared/delete.html"
    context_object_name = "tutorial"

    def get_queryset(self):
        return get_tutorial_comments_queryset(self.request.user)

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class RepliedToMyCommentsListView(SingleTableView):
    table_class = RepliedTutorialCommentTable
    template_name = "user/shared/list.html"

    @property
    def paginate_by(self):
        """Note: SingleTableView doesn't use get_paginate_by() currently, then
        defining paginate_by as a property is necessary to ensure it changes immediately.
        """
        return get_paginate_by()

    def get_queryset(self):
        return (
            TutorialComment.objects.filter(
                parent_comment__user=self.request.user
            )
            .select_related("tutorial", "parent_comment")
            .active_and_confirmed_comments()
            .active_confirmed_tutorials()
        )


class TutorialCommentLikedByOthersListView(SingleTableView):
    table_class = TutorialCommentUserRelationsTable
    template_name = "user/shared/list.html"

    @property
    def paginate_by(self):
        """Note: SingleTableView doesn't use get_paginate_by() currently, then
        defining paginate_by as a property is necessary to ensure it changes immediately.
        """
        return get_paginate_by()

    def get_queryset(self):
        return get_tutorial_comment_like_queryset().filter(
            comment__user=self.request.user
        )


class TutorialCommentLikedByMeListView(SingleTableView):
    table_class = TutorialCommentUserRelationsTable
    template_name = "user/shared/list.html"

    @property
    def paginate_by(self):
        """Note: SingleTableView doesn't use get_paginate_by() currently, then
        defining paginate_by as a property is necessary to ensure it changes immediately.
        """
        return get_paginate_by()

    def get_queryset(self):
        return get_tutorial_comment_like_queryset().filter(
            user=self.request.user
        )
