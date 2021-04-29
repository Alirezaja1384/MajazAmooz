""" Ajax urls """
from django.urls import path
from . import views

app_name = 'ajax'

urlpatterns = [
    path('insert_or_remove_tutorial_like', views.insert_or_delete_tutorial_like)
]
