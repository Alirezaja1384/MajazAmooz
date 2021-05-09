""" Authentication urls """
from django.urls import path

from .views import (
    LoginView, RegisterView,
    logout_view, logout_required_view
)


app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),
    path('logout_required/', logout_required_view, name='logout_required'),
]
