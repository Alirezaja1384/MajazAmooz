import json
from typing import Optional
from django.http import HttpRequest, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
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


@login_required
def tutorial_comment_create_view(request: HttpRequest):
    # If request is ajax and tutorial_id sent by client
    if request.method == "POST" and request.is_ajax():

        try:
            tutorial_comment = json.loads(request.body)
            tutorial_comment["user"] = request.user

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

        except (DatabaseError, ObjectDoesNotExist):
            return JsonResponse(
                {
                    "status": InsertOrDeleteStatus.ERROR,
                    "error": "خطایی در ثبت اطلاعات رخ داد",
                }
            )

        except Exception as ex:
            return JsonResponse(
                {"status": InsertOrDeleteStatus.ERROR, "error": ex.args}
            )

    return HttpResponseBadRequest()
