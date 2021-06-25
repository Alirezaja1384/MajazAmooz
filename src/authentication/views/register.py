from django.http import HttpRequest
from django.shortcuts import (render, redirect, reverse, resolve_url)
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages

from authentication.forms import RegisterForm
from utilities.view_utilities import LogoutRequiredMixin
from utilities.auth_utils import EmailConfirmationManager


UserModel = get_user_model()


class RegisterView(LogoutRequiredMixin, View):

    def get(self, request: HttpRequest):
        return render(request, 'authentication/register.html', {
            'form': RegisterForm(),
            'next': request.GET.get('next', '')
        })

    def post(self, request: HttpRequest):

        def _render_template(form, next_url):
            return render(request, 'authentication/register.html', {
                'form': form,
                'next': next_url
            })

        next_url = request.POST.get('next')
        form = RegisterForm(request.POST)

        if not form.is_valid():
            return _render_template(form, next_url)

        try:
            user = form.save()
            assert user is not None
        # If any unique field's value wasn't unique
        except AssertionError:
            form.add_error('', 'ثبت کاربر با مشکل مواجه شد')
            return _render_template(form, next_url)

        # Send confirmation uel
        confirm_manager = EmailConfirmationManager(user)

        uid_base64 = confirm_manager.get_uid_base64()
        token = confirm_manager.get_token()

        confirm_url = request.build_absolute_uri(
            resolve_url('authentication:confirm_email',
                        uid_base64=uid_base64, token=token)
        )

        send_email_result = confirm_manager.send_mail('mails/email_confirmation.html',
                                                      confirm_url, settings.DEFAULT_FROM_EMAIL)

        messages.success(request, 'ثبت نام با موفقیت انجام شد')
        if send_email_result:
            messages.success(request, 'ارسال ایمیل تایید حساب کاربری با موفقیت انجام شد')
        else:
            messages.error(request, 'ارسال ایمیل تایید حساب کاربری موفقیت آمیز نبود')

        # Redirect to login page
        login_url = reverse('authentication:login') + "?next=" + next_url
        return redirect(login_url)
