from django.http import HttpRequest
from django.shortcuts import render
from authentication.email_confirmation import EmailConfirmationManager


def confirm_email(request: HttpRequest, uid_base64, token):
    user = EmailConfirmationManager.validate(uid_base64, token)

    result = False
    if user:
        confirm_manager = EmailConfirmationManager(user)
        result = confirm_manager.confirm()

    return render(request, 'authentication/email_confirmation.html',
        {'result': result}
    )
