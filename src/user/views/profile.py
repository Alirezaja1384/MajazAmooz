from django.forms import ModelForm
from django.contrib import messages
from django.contrib.auth import get_user_model, views as auth_views
from django.views.generic import UpdateView
from django.shortcuts import reverse, redirect
from django.urls import reverse_lazy
from user.forms import UserProfileForm, PasswordChangeForm


SUCCESS_VIEW_NAME = "user:home"
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
            self.request, "اطلاعات پروفایل شما با موفقیت ویرایش شد"
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse(SUCCESS_VIEW_NAME)


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy("user:home")
    template_name = "user/shared/create_update.html"

    def form_valid(self, form):
        # Call main form_valid and get its result (redirection)
        result = super().form_valid(form)
        # Message user
        messages.success(self.request, "گذرواژه شما با موفقیت تغییر کرد شد")
        # Redirect user to success_url
        return result
