""" Ajax urls """
from django.urls import path
from . import views

app_name = 'ajax'

urlpatterns = [
    path('tutorial_like', views.tutorial_like_view),
    path('tutorial_upvote', views.tutorial_upvote_view),
    path('tutorial_downvote', views.tutorial_downvote_view),
]
