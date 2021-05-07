from django import forms
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class LoginForm(forms.Form):

    username_email = forms.CharField(max_length=254, label='نام کاربری یا ایمیل')

    password = forms.CharField(
        label="کلمه عبور",
        strip=False,
        widget=forms.PasswordInput
    )

    remember_me = forms.BooleanField(required=False, label='مرا به خاطر بسپار')
