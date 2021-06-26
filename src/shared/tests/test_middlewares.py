from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(
    LOGIN_REQUIRED_URLS=[r"^/user/(.)*$"],
    LOGIN_URL="/auth/login/",
)
class LoginRequiredMiddlewareTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testusername")

    def test_redirect_anonymous_user(self):
        response = self.client.get("/user/")
        self.assertEqual(response.status_code, 302)

    @override_settings(LOGIN_URL="/auth/register/")
    def test_redirect_login_url(self):
        response = self.client.get("/user/")
        self.assertRedirects(
            response,
            "/auth/register/?next=/user/",
        )

    def test_should_not_redirect_user(self):
        self.client.force_login(self.user)
        response = self.client.get("/user/")
        self.assertNotIn(response.status_code, [301, 302])

    def test_should_not_redirect_non_login_required(self):
        response = self.client.get("/")
        self.assertNotIn(response.status_code, [301, 302])


@override_settings(DEFAULT_USER_TZ="Australia/Eucla")
class TimezoneMiddlewareTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testusername")

    def test_use_default_user_tz(self):
        response = self.client.get("/")
        self.assertEqual(response.headers.get("Time-Zone"), "Australia/Eucla")

    def test_use_user_session(self):
        # To modify the session and then save it, it must be stored
        # in a variable first (because a new SessionStore is created
        # every time this property is accessed)
        # https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session["timezone"] = "America/Antigua"
        session.save()

        response = self.client.get("/")
        self.assertEqual(response.headers.get("Time-Zone"), "America/Antigua")
