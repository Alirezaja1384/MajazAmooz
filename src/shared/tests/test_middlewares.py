from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

User = get_user_model()


@override_settings(
    LOGIN_REQUIRED_URLS=[r"^/user/(.)*$"],
    LOGIN_URL="/auth/login/",
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "shared.middleware.LoginRequiredMiddleware",
    ],
)
class LoginRequiredMiddlewareTest(TestCase):
    def setUp(self):
        self.login_required_url = "/user/"
        self.login_url = "/auth/login/?next=" + self.login_required_url
        self.user = User.objects.create_user(username="testusername")

    def test_redirect_anonymous_user(self):
        """Should redirect anonymous user"""
        response = self.client.get(self.login_required_url)
        self.assertRedirects(response, self.login_url)

    def test_should_not_redirect_logged_in_user(self):
        """Should not redirect logged-in user"""
        self.client.force_login(self.user)
        response = self.client.get("/user/")
        self.assertNotIn(response.status_code, [301, 302])

    def test_should_not_redirect_non_login_required(self):
        """Should not redirect user if requested url doesn't
        exist in settings.LOGIN_REQUIRED_URLS.
        """
        response = self.client.get("/")
        self.assertNotIn(response.status_code, [301, 302])


@override_settings(
    DEFAULT_USER_TZ="Australia/Eucla",
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "shared.middleware.TimezoneMiddleware",
    ],
)
class TimezoneMiddlewareTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testusername")

    def test_use_default_user_tz(self):
        """Should use settings.DEFAULT_USER_TZ as user's default timezone."""
        response = self.client.get("/")
        self.assertEqual(response.headers.get("Time-Zone"), "Australia/Eucla")

    def test_use_user_session(self):
        """Should use user session's timezone instead of
        default timezone if specified.
        """
        # To modify the session and then save it, it must be stored
        # in a variable first (because a new SessionStore is created
        # every time this property is accessed)
        # https://docs.djangoproject.com/en/stable/topics/testing/tools/#django.test.Client.session
        session = self.client.session
        session["timezone"] = "America/Antigua"
        session.save()

        response = self.client.get("/")
        self.assertEqual(
            response.headers.get("Time-Zone"), session["timezone"]
        )
