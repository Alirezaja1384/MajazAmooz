""" Authentication urls """
from django.urls import path

from .views import LoginView


app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
]
