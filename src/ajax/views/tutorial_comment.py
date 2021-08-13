from typing import Optional
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from learning.models import (
    TutorialComment,
    TutorialCommentLike,
    TutorialCommentUpVote,
    TutorialCommentDownVote,
)
from ajax.forms import TutorialCommentForm
from ajax.views.shared import (
    AjaxView,
    InsertOrDeleteStatus,
    AjaxModelCreateDeleteView,
)

__all__ = [
    "like_view",
    "upvote_view",
    "downvote_view",
    "TutorialCommentCreateView",
]


class TutorialCommentUserRelationCreateDeleteView(AjaxModelCreateDeleteView):
    tutorial_comment: Optional[TutorialComment] = None

    def prepare_objects(self):
        tutorial_comment_id = self.data.get("comment_id")
        self.tutorial_comment = (
            TutorialComment.objects.active_and_confirmed_comments()
            .select_related("user")
            .get(pk=tutorial_comment_id)
        )

    def get_objects(self):
        return self.model.objects.filter(
            user=self.request.user, comment=self.tutorial_comment
        )

    def create_object(self):
        # Should automatically specify score and coin
        self.model.objects.create(
            user=self.request.user, comment=self.tutorial_comment
        )


class TutorialCommentCreateView(LoginRequiredMixin, AjaxView):
    def db_operation(self):
        self.data["user"] = self.request.user

        form = TutorialCommentForm(self.data)

        if form.is_valid():
            form.save()
        else:
            return JsonResponse(
                {
                    "status": InsertOrDeleteStatus.ERROR,
                    "error": form.errors,
                }
            )

        return JsonResponse({"status": InsertOrDeleteStatus.INSERTED})


BaseView = TutorialCommentUserRelationCreateDeleteView

like_view = BaseView.as_view(model=TutorialCommentLike)
upvote_view = BaseView.as_view(model=TutorialCommentUpVote)
downvote_view = BaseView.as_view(model=TutorialCommentDownVote)
