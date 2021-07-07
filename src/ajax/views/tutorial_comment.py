import json
from typing import Optional
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from constance import config
from learning.models import (
    TutorialComment,
    TutorialCommentUpVote,
    TutorialCommentDownVote,
    TutorialCommentLike,
)
from ajax.forms import TutorialCommentForm
from ajax.views.shared import (
    AjaxScoreCoinCreateDeleteView,
    InsertOrDeleteStatus,
    AjaxView,
)


class TutorialCommentUserRelationCreateDeleteView(
    AjaxScoreCoinCreateDeleteView
):
    tutorial_comment: Optional[TutorialComment] = None

    def set_parent_objects(self):
        tutorial_comment_id = int(
            json.loads(self.request.body).get("comment_id")
        )
        self.tutorial_comment = (
            TutorialComment.objects.active_and_confirmed_comments()
            .select_related("user")
            .get(id=tutorial_comment_id)
        )

    def get_objects(self):
        return self.model.objects.filter(
            user=self.request.user, comment=self.tutorial_comment
        )

    def create_object(self):
        self.model.objects.create(
            user=self.request.user,
            comment=self.tutorial_comment,
            score=self.score,
            coin=self.coin,
        )


class TutorialCommentLikeView(TutorialCommentUserRelationCreateDeleteView):
    model = TutorialCommentLike
    score = config.TUTORIAL_COMMENT_LIKE_SCORE
    coin = config.TUTORIAL_COMMENT_LIKE_COIN


class TutorialCommentUpVoteView(TutorialCommentUserRelationCreateDeleteView):
    model = TutorialCommentUpVote
    score = config.TUTORIAL_COMMENT_UPVOTE_SCORE
    coin = config.TUTORIAL_COMMENT_UPVOTE_COIN


class TutorialCommentDownVoteView(TutorialCommentUserRelationCreateDeleteView):
    model = TutorialCommentDownVote
    score = config.TUTORIAL_COMMENT_DOWNVOTE_SCORE
    coin = config.TUTORIAL_COMMENT_DOWNVOTE_COIN


class TutorialCommentCreateView(LoginRequiredMixin, AjaxView):
    def db_operation(self):
        tutorial_comment = json.loads(self.request.body)
        tutorial_comment["user"] = self.request.user

        form = TutorialCommentForm(tutorial_comment)

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
