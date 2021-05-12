from django.shortcuts import redirect
from django.http import HttpRequest
from django.conf import settings


class LogoutRequiredMixin():
    """
        Redirects user to LOGOUT_REQUIRED_URL
        set in settings if was authenticated
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):

        # If user was authenticated redirect
        # to logout required url
        try:
            logout_required_url = settings.LOGOUT_REQUIRED_URL
        except AttributeError as ex:
            msg = ("You must specify LOGOUT_REQUIRED_URL in your "
                   "settings module to use LogoutRequiredMixin")

            raise AttributeError(msg) from ex


        if request.user.is_authenticated:
            current_path = request.get_full_path()
            return redirect(logout_required_url + "?next=" + current_path)

        return super().dispatch(request, *args, **kwargs)