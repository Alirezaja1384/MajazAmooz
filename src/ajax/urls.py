""" Ajax urls """
from django.urls import path
from . import views

app_name = "ajax"

urlpatterns = [
    path("tutorial/like", views.TutorialLikeView.as_view()),
    path("tutorial/upvote", views.TutorialUpVoteView.as_view()),
    path("tutorial/downvote", views.TutorialDownVoteView.as_view()),
    path("tutorial_comment/like", views.TutorialCommentLikeView.as_view()),
    path("tutorial_comment/upvote", views.TutorialCommentUpVoteView.as_view()),
    path(
        "tutorial_comment/downvote",
        views.TutorialCommentDownVoteView.as_view(),
    ),
    path("tutorial_comment/create", views.tutorial_comment_create_view),
]
