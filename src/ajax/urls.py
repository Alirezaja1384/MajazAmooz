""" Ajax urls """
from django.urls import path
from .views import (
    tutorial_views,
    tutorial_comment_views,
)

app_name = "ajax"

urlpatterns = [
    path("tutorial/like", tutorial_views.like_view),
    path("tutorial/upvote", tutorial_views.upvote_view),
    path("tutorial/downvote", tutorial_views.downvote_view),
    path("tutorial_comment/like", tutorial_comment_views.like_view),
    path("tutorial_comment/upvote", tutorial_comment_views.upvote_view),
    path("tutorial_comment/downvote", tutorial_comment_views.downvote_view),
    path(
        "tutorial_comment/create",
        tutorial_comment_views.TutorialCommentCreateView.as_view(),
    ),
]
