""" Authentication urls """
from django.urls import path

from .views import (
    LoginView, RegisterView,
    confirm_email, logout_view,
    logout_required_view
)


app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm_email/<str:uid_base64>/<str:token>', confirm_email, name='confirm_email'),
    path('logout/', logout_view, name='logout'),
    path('logout_required/', logout_required_view, name='logout_required'),
]
