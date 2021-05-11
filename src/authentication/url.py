""" Authentication urls """
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from .views import (
    LoginView, RegisterView,
    confirm_email, logout_view,
    logout_required_view
)


app_name = 'authentication'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('confirm_email/<str:uid_base64>/<str:token>',
         confirm_email, name='confirm_email'),
    path('logout/', logout_view, name='logout'),
    path('logout_required/', logout_required_view, name='logout_required'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name="authentication/password_reset.html",
        email_template_name='mails/password_reset_html.html',
        html_email_template_name='mails/password_reset_html.html',
        success_url=reverse_lazy('authentication:password_reset_done')
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name="authentication/password_reset_done.html"),
        name='password_reset_done'),

    path('password_reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(
        template_name="authentication/password_reset_confirm.html",
        success_url=reverse_lazy('authentication:password_reset_complete')
    ), name='password_reset_confirm'),

    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="authentication/password_reset_complete.html"),
        name='password_reset_complete')
]
