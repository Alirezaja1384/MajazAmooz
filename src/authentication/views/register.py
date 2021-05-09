from django.http import HttpRequest
from django.shortcuts import (render, redirect, reverse)
from django.views.generic import View
from django.contrib.auth import get_user_model

from authentication.forms import RegisterForm
from utilities.view_utilities import LogoutRequiredMixin


UserModel = get_user_model()


class RegisterView(LogoutRequiredMixin, View):

    def get(self, request: HttpRequest):
        return render(request, 'authentication/register.html', {
            'form': RegisterForm(),
            'next': request.GET.get('next', '')
        })


    def post(self, request: HttpRequest):

        form = RegisterForm(request.POST)

        if not form.is_valid():
            return render(request, 'authentication/register.html', {
                'form': form,
                'next': request.POST.get('next', '')
            })

        # Register user
        form.save()

        next_url = request.POST.get('next')
        redirect_url = (reverse('authentication:login') +
                        "?next=" + next_url + "&register_success=True")

        return redirect(redirect_url)
