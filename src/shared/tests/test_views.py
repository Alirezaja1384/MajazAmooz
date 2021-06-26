from django.test import TestCase, RequestFactory, override_settings
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from shared.views import LogoutRequiredMixin

User = get_user_model()


@override_settings(LOGOUT_REQUIRED_URL="/auth/logout_required")
class LogoutRequiredMixinTest(TestCase):
    class LogoutNeededView(LogoutRequiredMixin, View):
        def get(self, request):
            return HttpResponse(status=200)

    def setUp(self):
        self.factory = RequestFactory()
        self.view = self.LogoutNeededView.as_view()
        self.user = User.objects.create(username="testuser")

    def test_logged_in_user(self):
        """
        Should redirect logged-in user.
        """
        request = self.factory.get("/logout_needed/")
        # Simulate logged-in user
        request.user = self.user

        response = self.view(request)
        self.assertRedirects(
            response,
            "/auth/logout_required?next=" + request.path,
            fetch_redirect_response=False,
        )

    def test_anonymous_user(self):
        """
        Should not redirect anonymous user.
        """
        request = self.factory.get("/logout_needed/")
        request.user = AnonymousUser()

        response = self.view(request)
        # Should not redirect user
        self.assertEqual(response.status_code, 200)

    def test_next_url_parameter(self):
        """
        Should not redirect if next parameter specified in url
        even if user is authenticated.
        """
        request = self.factory.get("/logout_needed/?next=/user/")
        request.user = self.user

        response = self.view(request)
        self.assertEqual(response.status_code, 200)
