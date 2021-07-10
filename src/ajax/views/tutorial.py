import json
from typing import Optional
from constance import config
from learning.models import (
    Tutorial,
    TutorialLike,
    TutorialUpVote,
    TutorialDownVote,
)
from ajax.views.shared import AjaxScoreCoinCreateDeleteView


class TutorialUserRelationCreateDeleteView(AjaxScoreCoinCreateDeleteView):
    tutorial: Optional[Tutorial] = None

    def set_parent_objects(self):
        tutorial_id = int(json.loads(self.request.body).get("tutorial_id"))
        self.tutorial = (
            Tutorial.objects.active_and_confirmed_tutorials()
            .select_related("author")
            .get(id=tutorial_id)
        )

    def get_objects(self):
        return self.model.objects.filter(
            user=self.request.user, tutorial=self.tutorial
        )

    def create_object(self):
        self.model.objects.create(
            user=self.request.user,
            tutorial=self.tutorial,
            score=self.score,
            coin=self.coin,
        )


class TutorialLikeView(TutorialUserRelationCreateDeleteView):
    model = TutorialLike
    score = config.TUTORIAL_LIKE_SCORE
    coin = config.TUTORIAL_LIKE_COIN


class TutorialUpVoteView(TutorialUserRelationCreateDeleteView):
    model = TutorialUpVote
    score = config.TUTORIAL_UPVOTE_SCORE
    coin = config.TUTORIAL_UPVOTE_COIN


class TutorialDownVoteView(TutorialUserRelationCreateDeleteView):
    model = TutorialDownVote
    score = config.TUTORIAL_DOWNVOTE_SCORE
    coin = config.TUTORIAL_DOWNVOTE_COIN
