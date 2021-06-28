from django.shortcuts import redirect
from django.http import HttpRequest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class LogoutRequiredMixin:
    """
    Redirects user to LOGOUT_REQUIRED_URL
    set in settings if authenticated and
    url doesn't have "next" pareneter
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):

        # If user was authenticated redirect
        # to logout required url
        try:
            logout_required_url = settings.LOGOUT_REQUIRED_URL
        except AttributeError as ex:
            msg = (
                "You must specify LOGOUT_REQUIRED_URL in your "
                "settings module to use LogoutRequiredMixin"
            )

            raise ImproperlyConfigured(msg) from ex

        # Url should not have 'next' parameter to redirect. Because if
        # user redirected to login page and url has 'next' parameter
        # it means user didn't have access and should login with another
        # account. Thus we should let user to login.
        if request.user.is_authenticated and not request.GET.get("next"):
            current_path = request.get_full_path()
            return redirect(logout_required_url + "?next=" + current_path)

        return super().dispatch(request, *args, **kwargs)
