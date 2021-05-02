""" Ajax urls """
from django.urls import path
from . import views

app_name = 'ajax'

urlpatterns = [
    path('tutorial/like', views.tutorial_like_view),
    path('tutorial/upvote', views.tutorial_upvote_view),
    path('tutorial/downvote', views.tutorial_downvote_view),

    path('tutorial_comment/create', views.tutorial_comment_create_view),
    path('tutorial_comment/like', views.tutorial_comment_like_view),
    path('tutorial_comment/upvote', views.tutorial_comment_upvote_view),
    path('tutorial_comment/downvote', views.tutorial_comment_downvote_view),
]
