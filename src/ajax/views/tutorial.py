from typing import Optional
from learning.models import (
    Tutorial,
    TutorialLike,
    TutorialUpVote,
    TutorialDownVote,
)
from ajax.views.shared import AjaxModelCreateDeleteView


__all__ = [
    "like_view",
    "upvote_view",
    "downvote_view",
]


class TutorialUserRelationCreateDeleteView(AjaxModelCreateDeleteView):
    tutorial: Optional[Tutorial] = None

    def prepare_objects(self):
        tutorial_id = self.data.get("tutorial_id")
        self.tutorial = (
            Tutorial.objects.active_and_confirmed_tutorials()
            .select_related("author")
            .get(pk=tutorial_id)
        )

    def get_objects(self):
        return self.model.objects.filter(
            user=self.request.user, tutorial=self.tutorial
        )

    def create_object(self):
        # Should automatically specify score and coin
        self.model.objects.create(
            user=self.request.user, tutorial=self.tutorial
        )


BaseView = TutorialUserRelationCreateDeleteView

like_view = BaseView.as_view(model=TutorialLike)
upvote_view = BaseView.as_view(model=TutorialUpVote)
downvote_view = BaseView.as_view(model=TutorialDownVote)
