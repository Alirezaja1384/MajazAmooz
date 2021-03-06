import re
from django.core import mail
from django.test import TestCase
from django.shortcuts import reverse, resolve_url
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from model_bakery import baker
from authentication.forms import RegisterForm, LoginForm

User = get_user_model()


class RegisterTest(TestCase):
    def setUp(self):
        self.next_url = "/login/"
        self.url = (
            reverse("authentication:register") + "?next=" + self.next_url
        )
        self.redirect_url = (
            reverse("authentication:login") + "?next=" + self.next_url
        )
        self.invalid_data = {"username": "", "email": "invalid email"}
        self.valid_data = {
            "next": self.next_url,
            "username": "username",
            "email": "user@email.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "str0ngP@ss",
            "password2": "str0ngP@ss",
        }

    def test_next_url_parameter(self):
        """Should pass a 'next' parameter in context with value of
        next url parameter.
        """
        response = self.client.get(self.url)
        context = response.context

        self.assertIn("next", context)
        self.assertEqual(context["next"], self.next_url)

    def test_form_type(self):
        """Should pass a RegisterForm as context form."""
        response = self.client.get(self.url)
        context = response.context

        self.assertIn("form", context)
        self.assertIsInstance(context["form"], RegisterForm)

    def test_invalid_data_form_error(self):
        """Should add form error when sent data is invalid."""
        response = self.client.post(self.url, data=self.invalid_data)
        context = response.context

        # Should add form errors
        self.assertIn("form", context)
        self.assertIsNotNone(context["form"].errors)

    def test_invalid_data_not_create_user(self):
        """Should not create user when sent data is invalid."""
        self.client.post(self.url, data=self.invalid_data)
        # Should not create user
        self.assertFalse(
            User.objects.filter(username=self.valid_data["username"]).exists()
        )

    def test_valid_data_create_user(self):
        """Should create user when sent data is valid."""
        self.client.post(self.url, data=self.valid_data)
        # Should create user
        self.assertTrue(
            User.objects.filter(username=self.valid_data["username"]).exists()
        )

    def test_valid_data_message(self):
        """Should send message when sent data is valid."""
        response = self.client.post(self.url, data=self.valid_data)
        # Should send message
        self.assertTrue(len(get_messages(response.wsgi_request)) > 0)

    def test_valid_data_redirect(self):
        """Should redirect user to 'next' when sent data is valid."""
        response = self.client.post(self.url, data=self.valid_data)
        # Should redirect to expected url
        self.assertRedirects(response, self.redirect_url)

    def test_send_confirmaton_email(self):
        """Should send email confirmation email when sent data is valid."""
        self.client.post(self.url, data=self.valid_data)
        self.assertTrue(len(mail.outbox) > 0)


class LoginTest(TestCase):
    def setUp(self):
        self.next_url = reverse("user:home")
        self.url = reverse("authentication:login") + "?next=" + self.next_url

        user_pass = "str0ngP@ss"
        self.user = baker.make(User)
        self.user.set_password(user_pass)
        self.user.save()

        self.invalid_data = {"username_email": "invalid", "password": "wrong"}
        self.valid_data_email = {
            "username_email": self.user.email,
            "password": user_pass,
            "next": self.next_url,
        }
        self.valid_data_username = {
            "username_email": self.user.username,
            "password": user_pass,
            "next": self.next_url,
        }

    def test_next_url_parameter(self):
        """Should pass a 'next' parameter in context with value of
        next url parameter.
        """
        response = self.client.get(self.url)
        context = response.context

        self.assertIn("next", context)
        self.assertEqual(context["next"], self.next_url)

    def test_form_type(self):
        """Should pass a LoginForm as context form."""
        response = self.client.get(self.url)
        context = response.context

        self.assertIn("form", context)
        self.assertIsInstance(context["form"], LoginForm)

    def test_invalid_data_form_error(self):
        """Should not redirect or authenticate user when credentials
        is invalid. It should add form error instead.
        """
        response = self.client.post(self.url, data=self.invalid_data)
        context = response.context

        # Should add error to form
        self.assertIn("form", context)
        self.assertIsNotNone(context["form"].errors)

    def test_invalid_data_not_authenticate(self):
        """Should not authenticate user when credentials is invalid."""
        response = self.client.post(self.url, data=self.invalid_data)

        # User should no be able to login without valid credentials
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_valid_data_by_username(self):
        """Should login user by username if credentials was valid."""
        response = self.client.post(self.url, data=self.valid_data_username)
        # Check user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_valid_data_by_email(self):
        """Should login user by email if credentials was valid."""
        response = self.client.post(self.url, data=self.valid_data_email)
        # Check user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_valid_data_redirect(self):
        """Should redirect user to 'next' url if credentials was valid."""
        response = self.client.post(self.url, data=self.valid_data_email)
        # Check redirects to expected url
        self.assertRedirects(response, self.next_url, target_status_code=200)


class LogoutTest(TestCase):
    def setUp(self):
        self.next_url = reverse("authentication:login")
        self.url = reverse("authentication:logout")

        self.user = baker.make(User)
        self.user.save()

    def test_logout(self):
        # Login
        self.client.force_login(self.user)
        # Try to logout by logout view
        response = self.client.post(self.url)

        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_context_next(self):
        # Login
        self.client.force_login(self.user)
        # Try to logout by logout view and get context
        context = self.client.post(
            self.url, data={"next": self.next_url}
        ).context

        self.assertIn("next", context)
        self.assertEqual(context["next"], self.next_url)


class ConfirmEmailTest(TestCase):
    def setUp(self):
        self.user_pk = self.register_user().pk

    def register_user(self):
        url = reverse("authentication:register")
        valid_data = {
            "username": "username",
            "email": "user@email.com",
            "first_name": "Test",
            "last_name": "User",
            "password1": "str0ngP@ss",
            "password2": "str0ngP@ss",
        }
        self.client.post(url, data=valid_data)
        return User.objects.get(username=valid_data["username"])

    def test_invalid_data(self):
        url = resolve_url(
            "authentication:confirm_email",
            uid_base64="invalid_uuid",
            token="invalid_token",
        )
        result = self.client.get(url).context["result"]

        # Context's result should be false
        self.assertFalse(result)
        # Should not confirm user email
        self.assertFalse(User.objects.get(pk=self.user_pk).email_confirmed)

    def test_valid_data(self):
        confirm_url_regex = r"/auth/confirm_email/.+/.+"
        # Search url regex in first email's body
        search = re.search(confirm_url_regex, mail.outbox[0].body)

        # Should find url
        self.assertIsNotNone(search)

        # Get matched url and call it
        confirm_url = search.group(0)
        result = self.client.get(confirm_url).context["result"]

        # Context's result should be true
        self.assertTrue(result)
        # Should confirm user email
        self.assertTrue(User.objects.get(pk=self.user_pk).email_confirmed)
