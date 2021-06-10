from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView
from django.shortcuts import (reverse, redirect)
from user.forms import UserProfileForm


SUCCESS_VIEW_NAME = 'user:home'
UserModel = get_user_model()


class UserProfileUpdateView(UpdateView):
    model = UserModel
    form_class = UserProfileForm

    template_name = "user/shared/create_update.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form: ModelForm):
        form.save()
        messages.success(
            self.request, 'اطلاعات پروفایل شما با موفقیت ویرایش شد')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)
