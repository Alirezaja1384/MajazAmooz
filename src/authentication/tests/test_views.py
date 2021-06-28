from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.messages import get_messages
from authentication.forms import RegisterForm


class RegisterTest(TestCase):
    def setUp(self):
        self.next_url = "/login/"
        self.url = (
            reverse("authentication:register") + "?next=" + self.next_url
        )
        self.redirect_url = (
            reverse("authentication:login") + "?next=" + self.next_url
        )
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
        response = self.client.get(self.url)
        context = response.context

        self.assertIn("next", context)
        self.assertEqual(context["next"], self.next_url)

    def test_register_form(self):
        response = self.client.get(self.url)
        context = response.context

        self.assertIn("form", context)
        self.assertIsInstance(context["form"], RegisterForm)

    def test_register_invalid_data(self):
        invalid_data = {"username": "", "email": "invalid email"}
        response = self.client.post(self.url, data=invalid_data)
        context = response.context

        self.assertIn("form", context)
        self.assertIsNotNone(context["form"].errors)

    def test_register_valid_data(self):
        response = self.client.post(self.url, data=self.valid_data)

        # Check redirects to expected url
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirect_url)

        # Check sends message
        self.assertTrue(len(get_messages(response.wsgi_request)) > 0)
