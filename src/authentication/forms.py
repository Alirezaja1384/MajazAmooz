from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


UserModel = get_user_model()


class LoginForm(forms.Form):

    username_email = forms.CharField(max_length=254, label='نام کاربری یا ایمیل')

    password = forms.CharField(
        label="کلمه عبور",
        strip=False,
        widget=forms.PasswordInput
    )

    remember_me = forms.BooleanField(required=False, label='مرا به خاطر بسپار')


class RegisterForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set all fields required
        for key in self.fields:
            self.fields[key].required = True


    class Meta:
        model = UserModel
        fields = ('username', 'email', 'first_name', 'last_name',)
        required_fields = '__all__'
