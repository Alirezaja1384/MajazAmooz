from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpRequest
from django.db.models import ObjectDoesNotExist
from django.contrib.auth import (
    authenticate, login,
    get_user_model
)

from authentication.forms import LoginForm
from shared.views import LogoutRequiredMixin


UserModel = get_user_model()


class LoginView(LogoutRequiredMixin, View):

    def get(self, request: HttpRequest):
        form = LoginForm()

        return render(request, 'authentication/login.html', {
            'form': form,
            'next': request.GET.get('next', '')
        })


    def post(self, request: HttpRequest):

        form = LoginForm(request.POST)

        if not form.is_valid():
            return render(request, 'authentication/login.html',  {
                'next': request.POST.get('next', ''),
                'form': form
            })

        username_email = form.cleaned_data["username_email"]
        password = form.cleaned_data["password"]

        try:
            # Try login by email
            user_by_email = UserModel.objects.get(email=username_email)
            user = authenticate(
                username=user_by_email.username, password=password)
        except ObjectDoesNotExist:
            # Try login by username
            user = authenticate(username=username_email, password=password)

        if user:
            # Login user
            login(request, user)

            # If user didn't check remember_me
            # session will expire on browser close
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)

            # If url has next parameter
            # and the url is local (starts with '/' )
            # redirect user to the next url
            next_url = request.POST.get("next")
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            # If next didn't exist or wasn't local
            # redirect to learning home
            return redirect("learning:home")
        else:
            form.add_error("", "نام کاربری یا رمز عبور اشتباه است")

        return render(request, "authentication/login.html",  {
            'next': request.POST.get('next', ''),
            'form': form
        })
